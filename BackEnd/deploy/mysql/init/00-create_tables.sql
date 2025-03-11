use graduation;

create table if not exists aerich
(
    id      int auto_increment
        primary key,
    version varchar(255) not null,
    app     varchar(100) not null,
    content json         not null
);

create table if not exists operationlog
(
    id          int auto_increment
        primary key,
    create_time datetime(6) default CURRENT_TIMESTAMP(6) not null comment '创建时间',
    update_time datetime(6) default CURRENT_TIMESTAMP(6) not null on update CURRENT_TIMESTAMP(6) comment '更新时间',
    order_no    int         default 999                  null comment '用来排序的序号',
    status      tinyint(1)  default 1                    not null comment 'True:启用 False:禁用',
    remark      varchar(255)                             null comment '备注描述',
    user_id     int                                      not null comment '用户ID',
    object_cls  varchar(255)                             not null comment '操作对象类',
    method      varchar(255)                             not null comment '操作方法',
    ip          varchar(32)                              null comment '访问IP',
    detail      json                                     not null comment '详细参数'
);

create table if not exists access
(
    id                    int auto_increment
        primary key,
    create_time           datetime(6) default CURRENT_TIMESTAMP(6) not null comment '创建时间',
    update_time           datetime(6) default CURRENT_TIMESTAMP(6) not null on update CURRENT_TIMESTAMP(6) comment '更新时间',
    path                  varchar(255)                             null comment '路径',
    component             varchar(255)                             null comment '组件',
    name                  varchar(255)                             not null comment '名称',
    title                 varchar(255)                             not null comment '标题',
    icon                  varchar(255)                             null comment '图标',
    is_button             tinyint(1)  default 0                    not null comment '是否为按钮',
    scopes                varchar(255)                             null comment '权限范围标识',
    parent_id             int         default 0                    not null comment '父id',
    order_no              int         default 999                  null comment '用来排序的序号',
    is_router             tinyint(1)  default 1                    not null comment '是否为前端路由',
    hide_menu             tinyint(1)  default 0                    not null comment '当前路由不再菜单显示',
    status                tinyint(1)  default 1                    not null comment 'True:启用 False:禁用',
    remark                varchar(255)                             null comment '备注描述',
    redirect              varchar(255)                             null comment '重定向',
    hide_children_in_menu tinyint(1)  default 0                    not null comment '隐藏所有子菜单',
    constraint name
        unique (name),
    constraint scopes
        unique (scopes),
    constraint title
        unique (title)
)
    comment '权限表';

create table if not exists role
(
    id          int auto_increment
        primary key,
    create_time datetime(6) default CURRENT_TIMESTAMP(6) not null comment '创建时间',
    update_time datetime(6) default CURRENT_TIMESTAMP(6) not null on update CURRENT_TIMESTAMP(6) comment '更新时间',
    role_name   varchar(15)                              not null comment '角色名称',
    order_no    int         default 999                  null comment '用来排序的序号',
    status      tinyint(1)  default 1                    not null comment 'True:启用 False:禁用',
    remark      varchar(255)                             null comment '备注描述'
)
    comment '角色表';

create table if not exists role_access
(
    role_id   int not null,
    access_id bigint not null,
    constraint role_access_ibfk_1
        foreign key (role_id) references role (id)
            on delete cascade,
    constraint role_access_ibfk_2
        foreign key (access_id) references access (id)
            on delete cascade
);

create index access_id
    on role_access (access_id);

create index role_id
    on role_access (role_id);

create table if not exists user
(
    id           int auto_increment
        primary key,
    create_time  datetime(6) default CURRENT_TIMESTAMP(6) not null comment '创建时间',
    update_time  datetime(6) default CURRENT_TIMESTAMP(6) not null on update CURRENT_TIMESTAMP(6) comment '更新时间',
    username     varchar(20)                              not null comment '用户名',
    password     varchar(255)                             not null comment '密码',
    nickname     varchar(255)                             null comment '昵称',
    email        varchar(255)                             null comment '邮箱',
    full_name    varchar(255)                             null comment '姓名',
    is_superuser tinyint(1)  default 0                    not null comment '是否为超级管理员',
    head_img     varchar(255)                             null comment '头像',
    gender       smallint    default 0                    not null comment 'unknown: 0
male: 1
female: 2',
    order_no     int         default 999                  null comment '用来排序的序号',
    status       tinyint(1)  default 1                    not null comment 'True:启用 False:禁用',
    remark       varchar(255)                             null comment '备注描述',
    constraint email
        unique (email),
    constraint username
        unique (username)
)
    comment '用户表';

create table if not exists profile
(
    id          int auto_increment
        primary key,
    create_time datetime(6) default CURRENT_TIMESTAMP(6) not null comment '创建时间',
    update_time datetime(6) default CURRENT_TIMESTAMP(6) not null on update CURRENT_TIMESTAMP(6) comment '更新时间',
    point       int         default 0                    not null comment '积分',
    user_id     int                                      not null,
    order_no    int         default 999                  null comment '用来排序的序号',
    status      tinyint(1)  default 1                    not null comment 'True:启用 False:禁用',
    remark      varchar(255)                             null comment '备注描述',
    constraint user_id
        unique (user_id),
    constraint fk_profile_user_80190c5a
        foreign key (user_id) references user (id)
            on delete cascade
)
    comment '用户扩展资料';

create table if not exists user_role
(
    user_id int not null,
    role_id int not null,
    constraint user_role_ibfk_1
        foreign key (user_id) references user (id)
            on delete cascade,
    constraint user_role_ibfk_2
        foreign key (role_id) references role (id)
            on delete cascade
);

create index role_id
    on user_role (role_id);

create index user_id
    on user_role (user_id);

create table if not exists channel
(
    id          int auto_increment
        primary key,
    hash_id     varchar(16)                           not null comment '散列url唯一id',
    create_time  datetime(6) default CURRENT_TIMESTAMP(6) not null comment '创建时间',
    update_time  datetime(6) default CURRENT_TIMESTAMP(6) not null on update CURRENT_TIMESTAMP(6) comment '更新时间',
    tvg_id varchar(100)                                null comment 'tvg-id',
    tvg_country   varchar(50)                             null comment '国家',
    tvg_language   varchar(20)                             null comment '语言',
    tvg_logo     varchar(255)                             null comment 'logo',
    group_title    varchar(50)                             null comment '分组',
    title     varchar(255)                            not null comment '频道标题',
    url     varchar(255)                              not null comment '资源URL',
    remark       varchar(255)                             null comment '备注描述',
    status       tinyint  default 1                   not null comment 'True:启用 False:禁用',
    del_flag      tinyint(4) UNSIGNED NOT NULL DEFAULT 0 COMMENT '逻辑删除标识',
    constraint hash_id
        unique (hash_id)
)
    comment '频道表';


create table if not exists channel_role
(
    role_id   int not null,
    channel_id int not null,
    constraint channel_role_ibfk_1
        foreign key (role_id) references role (id)
            on delete cascade,
    constraint channel_role_ibfk_2
        foreign key (channel_id) references channel (id)
            on delete cascade
);

create index role_id
    on channel_role (role_id);

create index channel_id
    on channel_role (channel_id);


CREATE TABLE sys_menu
(
    `id`              bigint(20)    	auto_increment                  comment '主键ID',
    `create_time`     datetime       default CURRENT_TIMESTAMP not null comment '创建时间',
    `update_time`     datetime       default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    `title`           varchar(255)       NOT NULL                        comment '名称',
    `component`       varchar(255)      NULL DEFAULT NULL               comment '组件',
    `parent_id`       bigint(20)        NOT NULL DEFAULT 0              comment '上级菜单ID(根节点设置为0)',
    `type`            int(11)       	NOT NULL DEFAULT 1              comment '菜单类型(参考MenuTypeEnum)',
    `scopes`      	  varchar(255)      NULL DEFAULT ''             comment '权限标识',
    `icon`            varchar(255)      NULL DEFAULT NULL               comment '图标',
    `order_no`        int(11)     	    NULL DEFAULT 1                  comment '排序',
    `status`          int(11)           NOT NULL DEFAULT 0              comment '状态(0=禁用 1=启用)',
    `redirect`        varchar(255)      NULL DEFAULT ''                 comment '外链地址',
    PRIMARY KEY (id) USING BTREE
) AUTO_INCREMENT = 1000
    comment '后台菜单';
SET @@auto_increment_increment=10; -- 将自动增长步长设为10
SET @@auto_increment_offset=1000; -- 将自动增长初始值设为1000

# type=0                type=1              type=2              type=3
# redirect=null         redirect=null       redirect=null       redirect=外链地址
# parentId=0            parentId=t0-id      parentId=t1-id      parentId=t0 or t1-id
# component=LAYOUT      component=path      component=LAYOUT    component=外链地址
# `/`path=name=时间戳    name=时间戳          `/`path=name        name=path=component

# 目录 component=LAYOUT  externalLink=null   path=/时间戳1   name=时间戳1
# 菜单 component=/path1    externalLink=null   path=/path1   name=时间戳
# 按钮 component=LAYOUT    externalLink=null   path=/时间戳1   name=时间戳1
# 外链 component=外链地址  externalLink=外链地址 path=外链地址   name=时间戳



# type=目录0 菜单1 按钮2 外链3
INSERT INTO graduation.sys_menu (id, create_time,update_time,title,component,parent_id,`type`,scopes,icon,order_no,status,redirect) VALUES
	 (10,'2022-08-06 06:35:55','2022-08-09 13:00:56','首页','LAYOUT',0,0,'Dashboard','ant-design:appstore-outlined',1,1,NULL),
	 (20,'2022-08-07 07:47:21','2022-08-09 21:14:06','仪表台','/dashboard/analysis/index',10,1,'Dashboard:analysis','ant-design:fund-outlined',2,1,NULL),
	 (30,'2022-08-06 06:45:37','2022-08-09 13:12:35','系统管理','LAYOUT',0,0,'Sys','ion:settings-outline',3,1,NULL),
	 (40,'2022-08-07 07:55:48','2022-08-09 13:12:35','账号管理','LAYOUT',30,1,'SysUser','ant-design:user-outlined',4,1,'/system/account/index'),
	 (50,'2022-08-06 14:14:21','2022-08-09 21:14:32','账号列表','LAYOUT',40,2,'account_list',NULL,5,1,NULL),
	 (60,'2022-08-06 14:14:21','2022-08-09 13:12:35','添加账号',NULL,40,2,'account_add',NULL,6,1,NULL),
	 (70,'2022-08-06 14:14:21','2022-08-09 13:12:35','删除账号',NULL,40,2,'account_delete',NULL,7,1,NULL),
	 (80,'2022-08-06 14:14:21','2022-08-09 13:12:35','修改账号',NULL,40,2,'account_update',NULL,8,1,NULL),
	 (90,'2022-08-06 14:14:21','2022-08-09 13:22:39','查看账号',NULL,40,2,'account_read',NULL,9,1,NULL),
	 (100,'2022-08-06 14:14:21','2022-08-09 13:12:36','分配角色下拉框',NULL,4,2,'role_options',NULL,10,1,NULL);
INSERT INTO graduation.sys_menu (id,create_time,update_time,title,component,parent_id,`type`,scopes,icon,order_no,status,redirect) VALUES
	 (110,'2022-08-06 13:15:33','2022-08-09 13:12:36','账号详情页','/system/account/AccountDetail',4,2,'',NULL,11,1,NULL),
	 (120,'2022-08-07 08:15:32','2022-08-09 13:12:35','角色管理','LAYOUT',3,2,'','ant-design:instagram-outlined',12,1,'/system/role/index'),
	 (130,'2022-08-06 14:14:21','2022-08-09 13:12:35','角色列表','/system/role/index',12,2,'role_list',NULL,13,1,NULL),
	 (140,'2022-08-06 14:14:21','2022-08-09 13:12:35','角色添加',NULL,12,2,'role_add',NULL,14,1,NULL),
	 (150,'2022-08-06 14:14:21','2022-08-09 13:12:35','角色删除',NULL,12,2,'role_delete',NULL,15,1,NULL),
	 (160,'2022-08-06 14:14:21','2022-08-09 13:12:35','角色修改',NULL,12,2,'role_update',NULL,16,1,NULL),
	 (170,'2022-08-06 14:14:21','2022-08-09 13:12:35','查看角色',NULL,12,2,'role_read',NULL,17,1,NULL),
	 (180,'2022-08-07 04:50:05','2022-08-09 13:12:35','角色状态',NULL,12,2,'role_status',NULL,18,1,NULL),
	 (190,'2022-08-07 04:50:05','2022-08-09 13:12:35','获取菜单树',NULL,12,2,'menu_tree',NULL,19,1,NULL),
	 (200,'2022-08-07 08:22:21','2022-08-09 13:12:36','菜单管理','LAYOUT',3,2,'','ant-design:appstore-filled',20,1,'/system/menu/index');
INSERT INTO graduation.sys_menu (id,create_time,update_time,title,component,parent_id,`type`,scopes,icon,order_no,status,redirect) VALUES
	 (210,'2022-08-06 14:14:21','2022-08-09 21:21:10','菜单列表','/system/menu/index',20,2,'menu_list',NULL,21,1,NULL),
	 (220,'2022-08-07 11:38:39','2022-08-09 13:12:35','修改菜单',NULL,20,2,'menu_update',NULL,22,1,NULL),
	 (230,'2022-08-09 13:25:27','2022-08-10 13:51:50','关于','LAYOUT',0,2,'','clarity:info-standard-line',25,1,'/about/index'),
	 (240,'2022-08-09 13:27:21','2022-08-10 13:51:50','关于页面','/sys/about/index',23,2,'',NULL,26,1,NULL),
	 (250,'2022-08-10 12:04:34','2022-08-10 13:51:50','系统日志','LAYOUT',3,2,'','clarity:flask-line',23,1,'/system/logs/index'),
	 (260,'2022-08-10 12:06:12','2022-08-10 13:51:50','日志列表','/system/operation_logs/index',25,2,'logs_list','clarity:flask-line',24,1,NULL);



# ************************************************************
INSERT INTO graduation.sys_menu (create_time,update_time,title,component,parent_id,`type`,scopes,icon,order_no,status,redirect,name,`path`) VALUES
	 ('2022-08-06 06:35:55','2023-03-10 01:17:12','首页','LAYOUT',0,0,'','ant-design:appstore-outlined',10,1,'/home/index','dashboard','/home'),
	 ('2022-08-07 07:47:21','2023-03-10 08:05:33','仪表台','/dashboard/analysis/index',10,1,'','ant-design:fund-outlined',10,1,NULL,'analysis','index'),
	 ('2022-08-06 06:45:37','2023-03-10 01:17:13','系统管理','LAYOUT',0,0,'','ion:settings-outline',20,1,NULL,'system','/system'),
	 ('2022-08-07 07:55:48','2023-03-10 09:07:10','账号管理','LAYOUT',30,1,'','ant-design:user-outlined',10,1,'/system/account/index','account_manage','account'),
	 ('2022-08-06 14:14:21','2023-03-10 02:16:40','账号列表','/system/account/index',40,1,'account_list',NULL,10,1,NULL,'get_all_users','index'),
	 ('2022-08-06 14:14:21','2023-03-10 01:17:25','添加账号',NULL,40,2,'account_add',NULL,20,1,NULL,'user_add',NULL),
	 ('2022-08-06 14:14:21','2023-03-10 01:17:55','删除账号',NULL,40,2,'account_delete',NULL,30,1,NULL,'user_del',NULL),
	 ('2022-08-06 14:14:21','2023-03-10 01:17:55','修改账号',NULL,40,2,'account_update',NULL,40,1,NULL,'user_update',NULL),
	 ('2022-08-06 14:14:21','2023-03-10 01:17:55','查看账号',NULL,40,2,'account_read',NULL,50,1,NULL,'get_user_by_id',NULL),
	 ('2022-08-06 14:14:21','2023-03-10 01:17:55','分配角色下拉框',NULL,40,2,'role_options',NULL,60,1,NULL,'all_roles_options',NULL);
INSERT INTO graduation.sys_menu (create_time,update_time,title,component,parent_id,`type`,scopes,icon,order_no,status,redirect,name,`path`) VALUES
	 ('2022-08-06 13:15:33','2023-03-10 02:16:40','账号详情页','/system/account/AccountDetail',40,1,'',NULL,70,1,NULL,'account_detail',':id'),
	 ('2022-08-07 08:15:32','2023-03-10 01:17:56','角色管理','LAYOUT',30,1,'','ant-design:instagram-outlined',20,1,'/system/role/index','role_manage','role'),
	 ('2022-08-06 14:14:21','2023-03-10 02:23:05','角色列表','/system/role/index',120,1,'role_list',NULL,10,1,NULL,'get_all_role','index'),
	 ('2022-08-06 14:14:21','2023-03-10 01:18:12','角色添加',NULL,120,2,'role_add',NULL,20,1,NULL,'create_role',NULL),
	 ('2022-08-06 14:14:21','2023-03-10 01:18:12','角色删除',NULL,120,2,'role_delete',NULL,30,1,NULL,'delete_role',NULL),
	 ('2022-08-06 14:14:21','2023-03-10 01:18:50','角色修改',NULL,120,2,'role_update',NULL,40,1,NULL,'update_role',NULL),
	 ('2022-08-06 14:14:21','2023-03-10 01:18:51','查看角色',NULL,120,2,'role_read',NULL,50,1,NULL,'read_role',NULL),
	 ('2022-08-07 04:50:05','2023-03-10 01:18:51','角色状态',NULL,120,2,'role_status',NULL,60,1,NULL,'set_role_status',NULL),
	 ('2022-08-07 04:50:05','2023-03-10 01:18:51','获取菜单树',NULL,120,2,'menu_tree',NULL,70,1,NULL,'get_menu_tree',NULL),
	 ('2022-08-07 08:22:21','2023-03-10 01:18:51','菜单管理','LAYOUT',30,1,'','ant-design:appstore-filled',30,1,'/system/menu/index','menu_manage','menu');
INSERT INTO graduation.sys_menu (create_time,update_time,title,component,parent_id,`type`,scopes,icon,order_no,status,redirect,name,`path`) VALUES
	 ('2022-08-06 14:14:21','2023-03-10 02:23:15','菜单列表','/system/menu/index',200,1,'menu_list',NULL,10,1,NULL,'get_all_access','index'),
	 ('2022-08-07 11:38:39','2023-03-10 01:18:52','修改菜单',NULL,200,2,'menu_update',NULL,20,1,NULL,'menu_update',NULL),
	 ('2022-08-09 13:25:27','2023-03-10 01:18:52','关于','LAYOUT',0,0,'','clarity:info-standard-line',30,1,'/about/index','about_manage','/about'),
	 ('2022-08-09 13:27:21','2023-03-10 02:23:57','关于页面','/sys/about/index',230,1,'',NULL,10,1,NULL,'about_index','index'),
	 ('2022-08-10 12:04:34','2023-03-10 01:18:52','系统日志','LAYOUT',30,1,'','clarity:flask-line',40,1,'/system/logs/index','logs_manage','logs'),
	 ('2022-08-10 12:06:12','2023-03-10 02:23:31','日志列表','/system/operation_logs/index',250,1,'logs_list','clarity:flask-line',10,1,NULL,'logs_list','index');
