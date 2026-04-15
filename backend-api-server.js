/**
 * 联想员工认证系统 - 后端 API 服务器
 *
 * 功能：
 * 1. 获取用户认证状态 (GET /api/user/cert-status)
 * 2. 提交认证申请 (POST /api/auth/submit)
 * 3. 获取用户认证历史 (GET /api/user/cert-history)
 *
 * 环境：Node.js + Express
 * 数据库：MySQL
 */

const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
const app = express();

// ========== 配置 ==========
app.use(cors());
app.use(express.json());

// MySQL 连接池
const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || 'password',
    database: process.env.DB_NAME || 'lenovo_cert',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// ========== 工具函数 ==========

/**
 * 获取用户ID（从 JWT Token 或 Cookie）
 * TODO: 实现真实的用户身份验证
 */
function getUserId(req) {
    // 演示：从 query 参数获取用户ID
    return req.query.uid || req.headers['x-user-id'] || 10001;
}

/**
 * 根据认证历史计算用户当前状态
 */
function calculateUserStatus(certHistory) {
    if (!certHistory || certHistory.length === 0) {
        return 'not-certified';
    }

    const lastCert = certHistory[certHistory.length - 1];

    // 检查是否有专业职称认证
    const hasSpecialist = certHistory.some(cert =>
        cert.cert_type.startsWith('specialist_') && cert.review_status === 'approved'
    );

    if (hasSpecialist) {
        return 'specialist-certified';
    }

    // 检查是否有基础企业认证
    const hasBasic = certHistory.some(cert =>
        cert.cert_type === 'basic' && cert.review_status === 'approved'
    );

    if (hasBasic) {
        return 'basic-certified';
    }

    return 'not-certified';
}

// ========== API 端点 ==========

/**
 * GET /api/user/cert-status
 * 获取用户的认证状态和历史信息
 */
app.get('/api/user/cert-status', async (req, res) => {
    try {
        const userId = getUserId(req);
        const connection = await pool.getConnection();

        // 查询用户的认证历史
        const [certHistory] = await connection.query(
            `SELECT * FROM certification_history
             WHERE uid = ?
             ORDER BY cert_number DESC`,
            [userId]
        );

        connection.release();

        // 如果没有认证历史，返回未认证状态
        if (!certHistory || certHistory.length === 0) {
            return res.json({
                success: true,
                status: 'not-certified',
                certCount: 0,
                lastCertData: null
            });
        }

        // 计算用户当前状态
        const status = calculateUserStatus(certHistory);
        const lastCert = certHistory[0];  // 最新的认证记录

        // 构建上一次认证的数据（用于预填）
        const lastCertData = {
            company: lastCert.company || '',
            position: lastCert.position || '',
            industry: lastCert.industry || '',
            specialty: lastCert.cert_type.replace('specialist_', '') || '',
            authMethod: lastCert.auth_method || ''
        };

        res.json({
            success: true,
            status: status,
            certCount: certHistory.length,
            lastCertData: lastCertData,
            lastCertDate: lastCert.submitted_at
        });

    } catch (error) {
        console.error('❌ 获取用户状态失败:', error);
        res.status(500).json({
            success: false,
            message: '获取用户状态失败',
            error: error.message
        });
    }
});

/**
 * POST /api/auth/submit
 * 提交认证申请
 */
app.post('/api/auth/submit', async (req, res) => {
    try {
        const userId = getUserId(req);
        const {
            flowType,           // 'first' | 'upgrade' | 'update'
            certNumber,         // 第几次认证
            isUpgrade,          // 是否为升级认证
            certType,           // 认证类型
            company,            // 企业名称
            position,           // 职位
            industry,           // 行业
            specialty,          // 专业职称
            authMethod,         // 认证方式
            filePath,           // 文件路径
            fileName,           // 文件名
            timestamp           // 提交时间
        } = req.body;

        const connection = await pool.getConnection();

        // 保存认证历史记录
        await connection.query(
            `INSERT INTO certification_history
             (uid, cert_number, cert_type, is_upgrade, company, position, industry,
              auth_method, file_path, file_name, review_status, submitted_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [
                userId,
                certNumber,
                certType,
                isUpgrade ? 1 : 0,
                company || null,
                position || null,
                industry || null,
                authMethod,
                filePath || null,
                fileName || null,
                'pending',  // 初始状态为待审核
                timestamp
            ]
        );

        // 更新用户认证状态
        const newStatus = calculateUserStatus([
            {
                cert_type: certType,
                review_status: 'approved'  // TODO: 实际应该等待审核
            }
        ]);

        // 检查是否存在该用户的状态记录
        const [statusRecord] = await connection.query(
            'SELECT * FROM user_cert_status WHERE uid = ?',
            [userId]
        );

        if (statusRecord.length > 0) {
            // 更新现有记录
            await connection.query(
                `UPDATE user_cert_status
                 SET status = ?, cert_count = ?, current_cert_type = ?,
                     last_cert_time = ?, updated_at = NOW()
                 WHERE uid = ?`,
                [newStatus, certNumber, certType, timestamp, userId]
            );
        } else {
            // 创建新记录
            await connection.query(
                `INSERT INTO user_cert_status
                 (uid, status, cert_count, current_cert_type, last_cert_time)
                 VALUES (?, ?, ?, ?, ?)`,
                [userId, newStatus, certNumber, certType, timestamp]
            );
        }

        connection.release();

        res.json({
            success: true,
            message: '认证申请已提交',
            newStatus: newStatus,
            certNumber: certNumber,
            certId: Date.now()  // 模拟认证记录ID
        });

        console.log(`✓ 用户 ${userId} 提交了第 ${certNumber} 次认证 (${certType})`);

    } catch (error) {
        console.error('❌ 提交认证申请失败:', error);
        res.status(500).json({
            success: false,
            message: '提交认证申请失败',
            error: error.message
        });
    }
});

/**
 * GET /api/user/cert-history
 * 获取用户完整的认证历史
 */
app.get('/api/user/cert-history', async (req, res) => {
    try {
        const userId = getUserId(req);
        const connection = await pool.getConnection();

        const [history] = await connection.query(
            `SELECT * FROM certification_history
             WHERE uid = ?
             ORDER BY cert_number DESC`,
            [userId]
        );

        connection.release();

        res.json({
            success: true,
            data: history || []
        });

    } catch (error) {
        console.error('❌ 获取认证历史失败:', error);
        res.status(500).json({
            success: false,
            message: '获取认证历史失败',
            error: error.message
        });
    }
});

// ========== 后台管理 API ==========

/**
 * GET /api/admin/users
 * 获取员工列表（带分页和筛选）
 */
app.get('/api/admin/users', async (req, res) => {
    try {
        const {
            page = 1,
            pageSize = 50,
            status = 'all',  // 'not-certified' | 'basic-certified' | 'specialist-certified' | 'all'
            certType = 'all'
        } = req.query;

        const connection = await pool.getConnection();
        const offset = (page - 1) * pageSize;

        // 构建 WHERE 条件
        let whereClause = '1=1';
        const params = [];

        if (status !== 'all') {
            whereClause += ' AND ucs.status = ?';
            params.push(status);
        }

        // 查询用户列表
        const [users] = await connection.query(
            `SELECT
                u.uid,
                u.name,
                u.phone,
                u.email,
                ucs.status,
                ucs.cert_count,
                ucs.current_cert_type,
                ucs.last_cert_time
             FROM users u
             LEFT JOIN user_cert_status ucs ON u.uid = ucs.uid
             WHERE ${whereClause}
             ORDER BY ucs.last_cert_time DESC
             LIMIT ? OFFSET ?`,
            [...params, parseInt(pageSize), offset]
        );

        // 获取总数
        const [countResult] = await connection.query(
            `SELECT COUNT(*) as total FROM users u
             LEFT JOIN user_cert_status ucs ON u.uid = ucs.uid
             WHERE ${whereClause}`,
            params
        );

        connection.release();

        const total = countResult[0].total;

        res.json({
            success: true,
            data: users,
            pagination: {
                page: parseInt(page),
                pageSize: parseInt(pageSize),
                total: total,
                totalPages: Math.ceil(total / pageSize)
            }
        });

    } catch (error) {
        console.error('❌ 获取员工列表失败:', error);
        res.status(500).json({
            success: false,
            message: '获取员工列表失败',
            error: error.message
        });
    }
});

/**
 * GET /api/admin/user/:uid/history
 * 获取指定用户的认证历史
 */
app.get('/api/admin/user/:uid/history', async (req, res) => {
    try {
        const { uid } = req.params;
        const connection = await pool.getConnection();

        const [history] = await connection.query(
            `SELECT * FROM certification_history
             WHERE uid = ?
             ORDER BY cert_number DESC`,
            [uid]
        );

        connection.release();

        res.json({
            success: true,
            data: history || []
        });

    } catch (error) {
        console.error('❌ 获取用户认证历史失败:', error);
        res.status(500).json({
            success: false,
            message: '获取用户认证历史失败',
            error: error.message
        });
    }
});

/**
 * POST /api/admin/cert/review
 * 审核认证申请
 */
app.post('/api/admin/cert/review', async (req, res) => {
    try {
        const {
            certId,         // 认证记录ID
            action,         // 'approve' | 'reject'
            reviewRemark    // 审核意见
        } = req.body;

        const reviewerId = getUserId(req);  // TODO: 实现真实的管理员身份验证
        const connection = await pool.getConnection();

        // 更新审核状态
        await connection.query(
            `UPDATE certification_history
             SET review_status = ?, reviewer_id = ?, review_remark = ?, reviewed_at = NOW()
             WHERE id = ?`,
            [
                action === 'approve' ? 'approved' : 'rejected',
                reviewerId,
                reviewRemark || null,
                certId
            ]
        );

        connection.release();

        res.json({
            success: true,
            message: `认证已${action === 'approve' ? '通过' : '驳回'}`
        });

        console.log(`✓ 管理员 ${reviewerId} ${action === 'approve' ? '通过' : '驳回'}了认证 #${certId}`);

    } catch (error) {
        console.error('❌ 审核认证失败:', error);
        res.status(500).json({
            success: false,
            message: '审核认证失败',
            error: error.message
        });
    }
});

// ========== 健康检查 ==========
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ========== 启动服务器 ==========
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
    console.log(`🚀 认证系统后端服务已启动 (端口: ${PORT})`);
    console.log(`📍 API 地址: http://localhost:${PORT}`);
    console.log(`   - GET  /api/user/cert-status - 获取用户认证状态`);
    console.log(`   - POST /api/auth/submit - 提交认证申请`);
    console.log(`   - GET  /api/user/cert-history - 获取认证历史`);
});

module.exports = app;
