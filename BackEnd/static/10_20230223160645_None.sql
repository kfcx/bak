-- upgrade --
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `access` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `status` BOOL NOT NULL  COMMENT 'True:启用 False:禁用' DEFAULT 1,
    `remark` VARCHAR(255)   COMMENT '备注描述',
    `path` VARCHAR(255)   COMMENT '路径',
    `name` VARCHAR(255) NOT NULL UNIQUE COMMENT '名称',
    `component` VARCHAR(255)   COMMENT '组件',
    `redirect` VARCHAR(255)   COMMENT '重定向',
    `title` VARCHAR(255) NOT NULL UNIQUE COMMENT '标题',
    `icon` VARCHAR(255)   COMMENT '图标',
    `hide_children_in_menu` BOOL NOT NULL  COMMENT '隐藏所有子菜单' DEFAULT 0,
    `hide_menu` BOOL NOT NULL  COMMENT '当前路由不再菜单显示' DEFAULT 0,
    `is_router` BOOL NOT NULL  COMMENT '是否为前端路由' DEFAULT 1,
    `is_button` BOOL NOT NULL  COMMENT '是否为按钮' DEFAULT 0,
    `scopes` VARCHAR(255)  UNIQUE COMMENT '权限范围标识',
    `parent_id` INT NOT NULL  COMMENT '父id' DEFAULT 0,
    `order_no` INT   COMMENT '用来排序的序号' DEFAULT 999
) CHARACTER SET utf8mb4 COMMENT='权限表';
CREATE TABLE IF NOT EXISTS `operationlog` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `status` BOOL NOT NULL  COMMENT 'True:启用 False:禁用' DEFAULT 1,
    `remark` VARCHAR(255)   COMMENT '备注描述',
    `user_id` INT NOT NULL  COMMENT '用户ID',
    `object_cls` VARCHAR(255) NOT NULL  COMMENT '操作对象类',
    `method` VARCHAR(255) NOT NULL  COMMENT '操作方法',
    `ip` VARCHAR(32)   COMMENT '访问IP',
    `detail` JSON NOT NULL  COMMENT '详细参数'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `role` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `status` BOOL NOT NULL  COMMENT 'True:启用 False:禁用' DEFAULT 1,
    `remark` VARCHAR(255)   COMMENT '备注描述',
    `role_name` VARCHAR(15) NOT NULL  COMMENT '角色名称',
    `order_no` INT   COMMENT '用来排序的序号' DEFAULT 999
) CHARACTER SET utf8mb4 COMMENT='角色表';
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `status` BOOL NOT NULL  COMMENT 'True:启用 False:禁用' DEFAULT 1,
    `remark` VARCHAR(255)   COMMENT '备注描述',
    `username` VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL  COMMENT '密码',
    `nickname` VARCHAR(255)   COMMENT '昵称',
    `phone` VARCHAR(11)  UNIQUE COMMENT '手机号',
    `email` VARCHAR(255)  UNIQUE COMMENT '邮箱',
    `full_name` VARCHAR(255)   COMMENT '姓名',
    `is_superuser` BOOL NOT NULL  COMMENT '是否为超级管理员' DEFAULT 0,
    `head_img` VARCHAR(255)   COMMENT '头像',
    `gender` SMALLINT NOT NULL  COMMENT 'unknown: 0\nmale: 1\nfemale: 2' DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='用户表';
CREATE TABLE IF NOT EXISTS `profile` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `status` BOOL NOT NULL  COMMENT 'True:启用 False:禁用' DEFAULT 1,
    `remark` VARCHAR(255)   COMMENT '备注描述',
    `point` INT NOT NULL  COMMENT '积分' DEFAULT 0,
    `user_id` INT NOT NULL UNIQUE,
    CONSTRAINT `fk_profile_user_80190c5a` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='用户扩展资料';
CREATE TABLE IF NOT EXISTS `role_access` (
    `role_id` INT NOT NULL,
    `access_id` INT NOT NULL,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`access_id`) REFERENCES `access` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_role` (
    `user_id` INT NOT NULL,
    `role_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
