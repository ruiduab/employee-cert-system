/**
 * 联想员工认证系统 - 数据库初始化脚本
 *
 * 创建所需的数据库表
 * 运行命令: mysql -u root -p < database-init.sql
 */

-- 创建数据库
CREATE DATABASE IF NOT EXISTS lenovo_cert CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lenovo_cert;

-- ========== 用户基本信息表 ==========
CREATE TABLE IF NOT EXISTS users (
    uid INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    idcard VARCHAR(18) UNIQUE NOT NULL COMMENT '身份证号',
    phone VARCHAR(11) UNIQUE NOT NULL COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户基本信息表';

-- ========== 用户认证状态表（新增）==========
CREATE TABLE IF NOT EXISTS user_cert_status (
    uid INT PRIMARY KEY COMMENT '用户ID',
    status VARCHAR(30) NOT NULL DEFAULT 'not-certified' COMMENT '认证状态: not-certified|basic-certified|specialist-certified',
    cert_count INT DEFAULT 0 COMMENT '认证次数',
    current_cert_type VARCHAR(50) COMMENT '当前认证类型',
    last_cert_time DATETIME COMMENT '最后一次认证时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES users(uid),
    INDEX idx_status (status),
    INDEX idx_last_cert_time (last_cert_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户认证状态表';

-- ========== 认证历史表（新增）==========
CREATE TABLE IF NOT EXISTS certification_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uid INT NOT NULL COMMENT '用户ID',
    cert_number INT NOT NULL COMMENT '第几次认证',
    cert_type VARCHAR(50) NOT NULL COMMENT '认证类型: basic|specialist_lawyer|specialist_design|...',
    is_upgrade BOOLEAN DEFAULT FALSE COMMENT '是否为升级认证',

    -- 认证信息
    company VARCHAR(100) COMMENT '企业名称',
    position VARCHAR(50) COMMENT '职位',
    industry VARCHAR(50) COMMENT '行业',
    auth_method VARCHAR(20) COMMENT '认证方式: email|contract|tax|other',

    -- 材料信息
    file_path VARCHAR(200) COMMENT '上传文件路径',
    file_name VARCHAR(100) COMMENT '上传文件名',

    -- 审核信息
    review_status VARCHAR(20) DEFAULT 'pending' COMMENT '审核状态: pending|approved|rejected',
    reviewer_id INT COMMENT '审核人ID',
    review_remark VARCHAR(500) COMMENT '审核意见',

    -- 时间戳
    submitted_at DATETIME NOT NULL COMMENT '提交时间',
    reviewed_at DATETIME COMMENT '审核时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid),
    INDEX idx_uid (uid),
    INDEX idx_cert_number (cert_number),
    INDEX idx_submitted_at (submitted_at),
    INDEX idx_review_status (review_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='认证历史表';

-- ========== 实名认证记录表 ==========
CREATE TABLE IF NOT EXISTS realname_auth (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uid INT NOT NULL COMMENT '用户ID',
    name VARCHAR(50) NOT NULL,
    idcard VARCHAR(18) NOT NULL,
    phone VARCHAR(11) NOT NULL,
    code VARCHAR(6) COMMENT '验证码',
    verified BOOLEAN DEFAULT FALSE,
    verified_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='实名认证记录表';

-- ========== 在职认证记录表 ==========
CREATE TABLE IF NOT EXISTS employee_auth (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uid INT NOT NULL COMMENT '用户ID',
    company VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verified_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='在职认证记录表';

-- ========== 材料认证记录表 ==========
CREATE TABLE IF NOT EXISTS material_auth (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uid INT NOT NULL COMMENT '用户ID',
    method VARCHAR(20) NOT NULL COMMENT '认证方式: email|contract|tax|other',
    email VARCHAR(100),
    file_path VARCHAR(200),
    verified BOOLEAN DEFAULT FALSE,
    verified_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='材料认证记录表';

-- ========== 审核日志表 ==========
CREATE TABLE IF NOT EXISTS audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uid INT NOT NULL COMMENT '用户ID',
    reviewer_id INT COMMENT '审核人ID',
    action VARCHAR(20) COMMENT '审核操作: approve|reject',
    remark VARCHAR(500) COMMENT '审核意见',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uid) REFERENCES users(uid),
    INDEX idx_uid (uid),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审核日志表';

-- ========== 示例数据 ==========

-- 插入测试用户
INSERT INTO users (uid, name, idcard, phone, email) VALUES
(10001, '张三', '110101199003071234', '13812345678', 'zhangsan@lenovo.com'),
(10002, '李四', '110101199004081234', '13912345678', 'lisi@lenovo.com'),
(10003, '王五', '110101199005091234', '13712345678', 'wangwu@lenovo.com');

-- 插入用户认证状态（演示）
INSERT INTO user_cert_status (uid, status, cert_count, current_cert_type, last_cert_time) VALUES
(10001, 'basic-certified', 1, 'basic', '2026-04-15 14:30:00'),
(10002, 'specialist-certified', 2, 'specialist_media', '2026-04-16 10:15:00'),
(10003, 'not-certified', 0, NULL, NULL);

-- 插入认证历史（演示）
INSERT INTO certification_history
(uid, cert_number, cert_type, is_upgrade, company, position, industry, auth_method, review_status, submitted_at, reviewed_at)
VALUES
(10001, 1, 'basic', 0, '联想（北京）有限公司', '产品经理', '互联网/信息技术', 'email', 'approved', '2026-04-15 14:30:00', '2026-04-15 15:00:00'),
(10002, 1, 'basic', 0, '联想集团有限公司', '设计师', '设计', 'email', 'approved', '2026-04-15 10:20:00', '2026-04-15 11:00:00'),
(10002, 2, 'specialist_media', 1, NULL, NULL, NULL, 'other', 'approved', '2026-04-16 10:15:00', '2026-04-16 11:00:00');

-- ========== 查询示例 ==========

-- 查看用户张三的认证状态
-- SELECT * FROM user_cert_status WHERE uid = 10001;

-- 查看用户张三的所有认证历史
-- SELECT * FROM certification_history WHERE uid = 10001 ORDER BY cert_number DESC;

-- 查看所有待审核的认证
-- SELECT * FROM certification_history WHERE review_status = 'pending' ORDER BY submitted_at DESC;

-- 查看所有已升级为专业认证的用户
-- SELECT * FROM certification_history WHERE is_upgrade = 1 AND review_status = 'approved';
