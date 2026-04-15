-- ============================================================
-- 企业职工认证系统 - 岗位和行业分类数据库初始化脚本
-- 数据来源：ramwin/china-public-data + job-titles-categories.json
-- ============================================================

-- 1. 创建行业分类表
CREATE TABLE IF NOT EXISTS industries (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '行业ID',
    code VARCHAR(10) UNIQUE COMMENT '行业代码',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '行业名称',
    en_name VARCHAR(100) COMMENT '英文名称',
    parent_id INT COMMENT '父级行业ID',
    level INT COMMENT '行业等级（1=一级，2=二级等）',
    description TEXT COMMENT '行业描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_name (name),
    INDEX idx_parent (parent_id),
    FOREIGN KEY (parent_id) REFERENCES industries(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行业分类表';

-- 2. 创建职位分类表
CREATE TABLE IF NOT EXISTS position_categories (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '职位分类ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '分类名称',
    en_name VARCHAR(100) COMMENT '英文分类名称',
    description TEXT COMMENT '分类描述',
    display_order INT DEFAULT 0 COMMENT '显示顺序',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位分类表';

-- 3. 创建岗位名称表（标准岗位库）
CREATE TABLE IF NOT EXISTS standard_positions (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '岗位ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '岗位名称',
    en_name VARCHAR(150) COMMENT '英文岗位名称',
    category_id INT COMMENT '职位分类ID',
    description TEXT COMMENT '岗位描述',
    keywords JSON COMMENT '关键词（用于搜索和自动完成）',
    related_industries JSON COMMENT '相关行业ID列表',
    skill_requirements TEXT COMMENT '技能要求',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_category (category_id),
    INDEX idx_active (is_active),
    FOREIGN KEY (category_id) REFERENCES position_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标准岗位库表';

-- ============================================================
-- 插入职位分类数据 (来自 job-titles-categories.json)
-- ============================================================

INSERT INTO position_categories (name, en_name, description, display_order) VALUES
('技术开发', 'Web Development', '互联网和软件开发相关岗位', 1),
('移动开发', 'Mobile Development', '移动应用开发相关岗位', 2),
('数据科学', 'Data Science', '数据分析和机器学习相关岗位', 3),
('设计', 'Design', '平面设计、UI/UX设计等相关岗位', 4),
('公关传播', 'Public Relations', '公关、传播、媒体相关岗位', 5),
('市场营销', 'Marketing', '营销、广告、品牌相关岗位', 6),
('人力资源', 'Human Resources', '人力资源管理相关岗位', 7),
('销售业务', 'Sales & Business Development', '销售和业务拓展相关岗位', 8),
('财务会计', 'Finance & Accounting', '财务和会计相关岗位', 9),
('产品管理', 'Product Management', '产品经理和项目管理岗位', 10);

-- ============================================================
-- 插入标准岗位数据（中文岗位库）
-- ============================================================

-- 技术开发类 (category_id = 1)
INSERT INTO standard_positions (name, en_name, category_id, keywords) VALUES
('产品经理', 'Product Manager', 10, '["产品", "经理", "PM"]'),
('产品总监', 'Director of Product', 10, '["产品", "总监"]'),
('产品助理', 'Product Assistant', 10, '["产品", "助理"]'),
('产品运营', 'Product Operations', 10, '["产品", "运营"]'),
('技术总监', 'Director of Technology', 1, '["技术", "总监", "CTO"]'),
('工程师', 'Engineer', 1, '["工程师", "技术"]'),
('开发工程师', 'Development Engineer', 1, '["开发", "工程师"]'),
('前端工程师', 'Frontend Engineer', 1, '["前端", "工程师", "Frontend"]'),
('后端工程师', 'Backend Engineer', 1, '["后端", "工程师", "Backend"]'),
('全栈工程师', 'Full Stack Engineer', 1, '["全栈", "工程师"]'),
('架构师', 'Architect', 1, '["架构", "架构师"]'),
('技术主管', 'Technical Lead', 1, '["技术", "主管", "Lead"]'),
('软件工程师', 'Software Engineer', 1, '["软件", "工程师"]'),
('程序员', 'Programmer', 1, '["程序员", "开发"]'),
('开发者', 'Developer', 1, '["开发", "开发者"]'),

-- 移动开发类 (category_id = 2)
('iOS开发工程师', 'iOS Developer', 2, '["iOS", "开发", "工程师"]'),
('Android开发工程师', 'Android Developer', 2, '["Android", "开发", "工程师"]'),
('小程序开发', 'Mini Program Developer', 2, '["小程序", "开发"]'),
('移动端开发', 'Mobile Developer', 2, '["移动", "开发"]'),

-- 设计类 (category_id = 4)
('设计师', 'Designer', 4, '["设计", "设计师"]'),
('平面设计师', 'Graphic Designer', 4, '["平面", "设计"]'),
('UI设计师', 'UI Designer', 4, '["UI", "设计"]'),
('交互设计师', 'Interaction Designer', 4, '["交互", "设计"]'),
('视觉设计师', 'Visual Designer', 4, '["视觉", "设计"]'),
('用户体验设计师', 'UX Designer', 4, '["UX", "用户体验", "设计"]'),

-- 销售类 (category_id = 8)
('销售经理', 'Sales Manager', 8, '["销售", "经理"]'),
('销售总监', 'Sales Director', 8, '["销售", "总监"]'),
('业务经理', 'Business Manager', 8, '["业务", "经理"]'),
('客户经理', 'Account Manager', 8, '["客户", "经理"]'),
('渠道经理', 'Channel Manager', 8, '["渠道", "经理"]'),
('销售代表', 'Sales Representative', 8, '["销售", "代表"]'),

-- 市场营销类 (category_id = 6)
('市场经理', 'Marketing Manager', 6, '["市场", "经理"]'),
('市场总监', 'Marketing Director', 6, '["市场", "总监"]'),
('品牌经理', 'Brand Manager', 6, '["品牌", "经理"]'),
('内容运营', 'Content Operations', 6, '["内容", "运营"]'),
('社区运营', 'Community Operations', 6, '["社区", "运营"]'),

-- 人力资源类 (category_id = 7)
('人力资源', 'Human Resources', 7, '["人力", "资源", "HR"]'),
('人力资源经理', 'HR Manager', 7, '["人力", "经理"]'),
('行政', 'Administration', 7, '["行政"]'),
('招聘', 'Recruiter', 7, '["招聘", "招聘专员"]'),

-- 财务会计类 (category_id = 9)
('财务', 'Finance', 9, '["财务"]'),
('财务经理', 'Finance Manager', 9, '["财务", "经理"]'),
('成本会计', 'Cost Accountant', 9, '["成本", "会计"]'),
('税务经理', 'Tax Manager', 9, '["税务", "经理"]'),
('会计', 'Accountant', 9, '["会计"]'),

-- 法律类
('法律顾问', 'Legal Counsel', 6, '["法律", "顾问"]'),
('法务', 'Legal Affairs', 6, '["法务"]'),
('律师', 'Lawyer', 6, '["律师"]'),
('合规经理', 'Compliance Manager', 6, '["合规", "经理"]'),

-- 运营管理类 (category_id = 10)
('项目经理', 'Project Manager', 10, '["项目", "经理"]'),
('项目总监', 'Project Director', 10, '["项目", "总监"]'),
('运营经理', 'Operations Manager', 10, '["运营", "经理"]'),
('供应链经理', 'Supply Chain Manager', 10, '["供应链", "经理"]'),

-- 制造类
('质量经理', 'Quality Manager', 10, '["质量", "经理"]'),
('制造工程师', 'Manufacturing Engineer', 1, '["制造", "工程师"]'),
('工业工程师', 'Industrial Engineer', 1, '["工业", "工程师"]'),
('制造经理', 'Manufacturing Manager', 10, '["制造", "经理"]'),

-- 采购物流类
('采购经理', 'Procurement Manager', 10, '["采购", "经理"]'),
('采购总监', 'Procurement Director', 10, '["采购", "总监"]'),
('物流经理', 'Logistics Manager', 10, '["物流", "经理"]'),
('仓储经理', 'Warehouse Manager', 10, '["仓储", "经理"]'),

-- 高管类 (category_id = 10)
('部门经理', 'Department Manager', 10, '["部门", "经理"]'),
('总经理', 'General Manager', 10, '["总经理", "GM"]'),
('董事长', 'Chairman', 10, '["董事长"]'),
('总裁', 'President', 10, '["总裁"]'),
('首席执行官', 'CEO', 10, '["CEO", "首席执行官"]'),

-- 数据科学类 (category_id = 3)
('数据科学家', 'Data Scientist', 3, '["数据", "科学家"]'),
('数据分析师', 'Data Analyst', 3, '["数据", "分析", "分析师"]'),
('算法工程师', 'Algorithm Engineer', 3, '["算法", "工程师", "机器学习"]'),
('机器学习工程师', 'Machine Learning Engineer', 3, '["机器学习", "工程师"]'),

-- 实习类
('实习生', 'Intern', 1, '["实习", "实习生"]');

-- ============================================================
-- 插入主要行业分类数据（中国国民经济行业分类简化版）
-- ============================================================

-- 第一级行业分类
INSERT INTO industries (code, name, en_name, level) VALUES
('A', '农、林、牧、渔业', 'Agriculture, Forestry, Animal Husbandry and Fishery', 1),
('B', '采矿业', 'Mining', 1),
('C', '制造业', 'Manufacturing', 1),
('D', '电力、热力、燃气及水生产和供应业', 'Electric Power, Heat, Gas and Water Production and Supply', 1),
('E', '建筑业', 'Construction', 1),
('F', '批发和零售业', 'Wholesale and Retail Trade', 1),
('G', '交通运输、仓储和邮政业', 'Transportation, Warehousing and Postal Services', 1),
('H', '住宿和餐饮业', 'Accommodation and Catering', 1),
('I', '信息传输、软件和信息技术服务业', 'Information Transmission, Software and Information Technology Services', 1),
('J', '金融业', 'Financial Services', 1),
('K', '房地产业', 'Real Estate', 1),
('L', '租赁和商务服务业', 'Leasing and Business Services', 1),
('M', '科学研究和技术服务业', 'Scientific Research and Technical Services', 1),
('N', '水利、环境和公共设施管理业', 'Water Conservancy, Environment and Public Facilities Management', 1),
('O', '居民服务、修理和其他服务业', 'Resident Services, Repair and Other Services', 1),
('P', '教育', 'Education', 1),
('Q', '卫生和社会工作', 'Health and Social Work', 1),
('R', '文化、体育和娱乐业', 'Culture, Sports and Entertainment', 1),
('S', '公共管理、社会保障和社会组织', 'Public Management, Social Security and Social Organizations', 1),
('T', '国际组织', 'International Organizations', 1);

-- 第二级行业分类（主要行业）
INSERT INTO industries (code, name, en_name, parent_id, level) VALUES
-- 制造业下的二级分类
('C01', '农副食品加工业', 'Food Processing Industry',
    (SELECT id FROM industries WHERE code='C'), 2),
('C02', '食品制造业', 'Food Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C03', '烟草制品业', 'Tobacco Products',
    (SELECT id FROM industries WHERE code='C'), 2),
('C04', '纺织业', 'Textile Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C05', '服装、服饰制造业', 'Garment Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C06', '皮毛、皮革及其制品和制鞋业', 'Leather and Footwear',
    (SELECT id FROM industries WHERE code='C'), 2),
('C07', '木材加工和木、竹、藤、棕、草制品业', 'Wood Processing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C08', '纸浆、纸和纸制品业', 'Paper Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C09', '印刷和记录媒体复制业', 'Printing and Media',
    (SELECT id FROM industries WHERE code='C'), 2),
('C10', '焦炭、油品、核燃料加工业', 'Coking and Oil Processing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C11', '化学原料和化学制品制造业', 'Chemical Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C12', '医药制造业', 'Pharmaceutical Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C13', '化学纤维制造业', 'Chemical Fiber Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C14', '橡胶和塑料制品业', 'Rubber and Plastic Products',
    (SELECT id FROM industries WHERE code='C'), 2),
('C15', '非金属矿物制品业', 'Non-metallic Mineral Products',
    (SELECT id FROM industries WHERE code='C'), 2),
('C16', '黑色金属冶炼和压延加工业', 'Ferrous Metal Smelting',
    (SELECT id FROM industries WHERE code='C'), 2),
('C17', '有色金属冶炼和压延加工业', 'Non-ferrous Metal Smelting',
    (SELECT id FROM industries WHERE code='C'), 2),
('C18', '金属制品业', 'Metal Products',
    (SELECT id FROM industries WHERE code='C'), 2),
('C19', '通用设备制造业', 'General Equipment Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C20', '专用设备制造业', 'Specialized Equipment Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C21', '汽车制造业', 'Automobile Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C22', '铁道、船舶、航空航天和其他运输设备制造业', 'Transportation Equipment',
    (SELECT id FROM industries WHERE code='C'), 2),
('C23', '电气机械和器材制造业', 'Electrical Machinery',
    (SELECT id FROM industries WHERE code='C'), 2),
('C24', '计算机、通信和其他电子设备制造业', 'Computer and Electronics',
    (SELECT id FROM industries WHERE code='C'), 2),
('C25', '仪器仪表制造业', 'Instrument Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),
('C26', '其他制造业', 'Other Manufacturing',
    (SELECT id FROM industries WHERE code='C'), 2),

-- 信息技术和软件服务业
('I01', '软件开发', 'Software Development',
    (SELECT id FROM industries WHERE code='I'), 2),
('I02', '信息技术咨询服务', 'IT Consulting Services',
    (SELECT id FROM industries WHERE code='I'), 2),
('I03', '互联网和相关服务', 'Internet and Related Services',
    (SELECT id FROM industries WHERE code='I'), 2),
('I04', '数据处理和存储服务', 'Data Processing Services',
    (SELECT id FROM industries WHERE code='I'), 2),

-- 金融业
('J01', '银行业', 'Banking',
    (SELECT id FROM industries WHERE code='J'), 2),
('J02', '证券业', 'Securities',
    (SELECT id FROM industries WHERE code='J'), 2),
('J03', '保险业', 'Insurance',
    (SELECT id FROM industries WHERE code='J'), 2),
('J04', '其他金融服务', 'Other Financial Services',
    (SELECT id FROM industries WHERE code='J'), 2),

-- 房地产业
('K01', '房地产开发经营', 'Real Estate Development',
    (SELECT id FROM industries WHERE code='K'), 2),
('K02', '物业管理', 'Property Management',
    (SELECT id FROM industries WHERE code='K'), 2),

-- 教育
('P01', '学前教育', 'Preschool Education',
    (SELECT id FROM industries WHERE code='P'), 2),
('P02', '初等教育', 'Primary Education',
    (SELECT id FROM industries WHERE code='P'), 2),
('P03', '中等教育', 'Secondary Education',
    (SELECT id FROM industries WHERE code='P'), 2),
('P04', '高等教育', 'Higher Education',
    (SELECT id FROM industries WHERE code='P'), 2),
('P05', '其他教育', 'Other Education',
    (SELECT id FROM industries WHERE code='P'), 2),

-- 卫生和社会工作
('Q01', '医疗卫生', 'Medical Services',
    (SELECT id FROM industries WHERE code='Q'), 2),
('Q02', '社会工作', 'Social Work',
    (SELECT id FROM industries WHERE code='Q'), 2);

-- ============================================================
-- 更新标准岗位与行业的关联关系
-- ============================================================

-- 技术类岗位关联行业
UPDATE standard_positions SET related_industries = '[1, 4, 5, 6, 7, 8, 9]'
WHERE name IN ('前端工程师', '后端工程师', '全栈工程师', '开发工程师', '软件工程师');

UPDATE standard_positions SET related_industries = '[1, 3, 4, 5]'
WHERE name IN ('产品经理', '产品总监', '产品运营');

UPDATE standard_positions SET related_industries = '[1, 2, 3, 4, 5, 6, 7, 8, 9]'
WHERE name IN ('项目经理', '项目总监', '运营经理');

-- ============================================================
-- 创建视图（可选）：便捷查询岗位和行业的关联
-- ============================================================

CREATE OR REPLACE VIEW v_positions_with_categories AS
SELECT
    sp.id,
    sp.name,
    sp.en_name,
    pc.name AS category_name,
    pc.en_name AS category_en_name,
    sp.keywords,
    sp.is_active
FROM standard_positions sp
LEFT JOIN position_categories pc ON sp.category_id = pc.id
WHERE sp.is_active = TRUE
ORDER BY pc.display_order, sp.name;

-- ============================================================
-- 创建索引以优化查询性能
-- ============================================================

ALTER TABLE standard_positions ADD FULLTEXT INDEX ft_name (name, en_name);
ALTER TABLE industries ADD FULLTEXT INDEX ft_name_industry (name, en_name);
ALTER TABLE position_categories ADD FULLTEXT INDEX ft_name_category (name, en_name);

-- ============================================================
-- 初始化完成
-- ============================================================

-- 统计信息
SELECT '行业分类总数' AS metric, COUNT(*) AS count FROM industries
UNION ALL
SELECT '职位分类总数', COUNT(*) FROM position_categories
UNION ALL
SELECT '标准岗位总数', COUNT(*) FROM standard_positions
UNION ALL
SELECT '启用的岗位数', COUNT(*) FROM standard_positions WHERE is_active = TRUE;
