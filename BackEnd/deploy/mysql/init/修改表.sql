use graduation;

# 在 RBAC 模型中，用户、角色、菜单表之间的关系通常是这样的：
#
# 1. 用户表（User）：存储用户的基本信息，如用户名、密码、邮箱等。
# 2. 角色表（Role）：存储角色的基本信息，如角色名、角色描述等。
# 3. 菜单表（Menu）：存储菜单的基本信息，如菜单名、菜单 URL 等。
# 4. 用户角色关系表（UserRole）：用于建立用户和角色之间的多对多关系，每个记录表示一个用户和一个角色之间的关系。
# 5. 角色菜单关系表（RoleMenu）：用于建立角色和菜单之间的多对多关系，每个记录表示一个角色和一个菜单之间的关系。
#
# 通过这些表之间的关系，可以实现 RBAC 模型中的权限控制。具体来说，每个用户可以被分配一个或多个角色，每个角色可以被分配一个或多个菜单，用户可以访问其被分配的角色所拥有的菜单。这样，就可以实现对系统中各个功能模块的权限控制，确保用户只能访问其被授权的功能。


create table if not exists aerich
(
    id      int auto_increment
        primary key,
    version varchar(255) not null,
    app     varchar(100) not null,
    content json         not null
);

create table if not exists profile
(
    id          int auto_increment
        primary key,
    create_time datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
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

create table if not exists operationlog
(
    id          int auto_increment
        primary key,
    create_time datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    order_no    int         default 999                  null comment '用来排序的序号',
    status      tinyint(1)  default 1                    not null comment 'True:启用 False:禁用',
    remark      varchar(255)                             null comment '备注描述',
    user_id     int                                      not null comment '用户ID',
    object_cls  varchar(255)                             not null comment '操作对象类',
    method      varchar(255)                             not null comment '操作方法',
    ip          varchar(32)                              null comment '访问IP',
    detail      json                                     not null comment '详细参数'
)
    comment '操作日志表';

create table if not exists access
(
    id                    int auto_increment
        primary key,
    create_time           datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time           datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
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
    create_time datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    role_name   varchar(15)                              not null comment '角色名称',
    order_no    int         default 999                  null comment '用来排序的序号',
    status      tinyint(1)  default 1                    not null comment 'True:启用 False:禁用',
    remark      varchar(255)                             null comment '备注描述'
)
    comment '角色表';

create table if not exists role_access
(
    role_id   int    not null,
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
    create_time  datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time  datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
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
    id           int auto_increment
        primary key,
    hash_id      varchar(16)                              not null comment '散列url唯一id',
    create_time  datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time  datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    tvg_id       varchar(100)                             null comment 'tvg-id',
    tvg_country  varchar(50)                              null comment '国家',
    tvg_language varchar(20)                              null comment '语言',
    tvg_logo     varchar(255)                             null comment 'logo',
    group_title  varchar(50)                              null comment '分组',
    title        varchar(255)                             not null comment '频道标题',
    url          varchar(255)                             not null comment '资源URL',
    remark       varchar(255)                             null comment '备注描述',
    status       tinyint     default 1                    not null comment 'True:启用 False:禁用',
    del_flag     tinyint(4) UNSIGNED                      NOT NULL DEFAULT 0 COMMENT '逻辑删除标识',
    constraint hash_id
        unique (hash_id)
)
    comment '频道表';


CREATE TABLE sys_menu
(
    `id`          bigint(20) auto_increment comment '主键ID',
    `create_time` datetime              default CURRENT_TIMESTAMP not null comment '创建时间',
    `update_time` datetime              default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    `title`       varchar(255) NOT NULL comment '名称',
    `component`   varchar(255) NULL     DEFAULT NULL comment '组件',
    `parent_id`   bigint(20)   NOT NULL DEFAULT 0 comment '上级菜单ID(根节点设置为0)',
    `type`        int(11)      NOT NULL DEFAULT 1 comment '菜单类型(参考MenuTypeEnum)',
    `scopes`      varchar(255) NULL     DEFAULT '' comment '权限标识',
    `icon`        varchar(255) NULL     DEFAULT NULL comment '图标',
    `order_no`    int(11)      NULL     DEFAULT 1 comment '排序',
    `status`      int(11)      NOT NULL DEFAULT 0 comment '状态(0=禁用 1=启用)',
    `redirect`    varchar(255) NULL     DEFAULT '' comment '外链地址',
    PRIMARY KEY (id) USING BTREE
) AUTO_INCREMENT = 1000
    comment '后台菜单';
SET @@auto_increment_increment = 10; -- 将自动增长步长设为10
SET @@auto_increment_offset = 1000;
-- 将自动增长初始值设为1000

# type=0                type=1              type=2              type=3
# redirect=null         redirect=null       redirect=null       redirect=外链地址
# parentId=0            parentId=t0-id      parentId=t1-id      parentId=t0 or t1-id
# component=LAYOUT      component=path      component=LAYOUT    component=外链地址
# `/`path=name=时间戳    name=时间戳          `/`path=name        name=path=component

# 目录 component=LAYOUT  externalLink=null   path=/时间戳1   name=时间戳1
# 菜单 component=/path1    externalLink=null   path=/path1   name=时间戳
# 按钮 component=LAYOUT    externalLink=null   path=/时间戳1   name=时间戳1
# 外链 component=外链地址  externalLink=外链地址 path=外链地址   name=时间戳