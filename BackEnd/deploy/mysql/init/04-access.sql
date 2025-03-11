INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (1, '2022-08-06 06:35:55.848803', '2022-08-09 13:00:56.472697', '/home', 'LAYOUT', 'dashboard', '首页', 'bx:bx-home', 0, null, 0, 1, 1, 0, 1, null, '/home/index', 1);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (2, '2022-08-07 07:47:21.965801', '2022-08-09 21:14:06.339881', 'index', '/dashboard/analysis/index', 'analysis', '仪表台', null, 0, null, 1, 2, 1, 0, 1, '首页嘛，每个人都要看的', null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (3, '2022-08-06 06:45:37.135206', '2022-08-09 13:12:35.918888', '/system', 'LAYOUT', 'system', '系统管理', 'ion:settings-outline', 0, null, 0, 3, 1, 0, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (4, '2022-08-07 07:55:48.829017', '2022-08-09 13:12:35.987713', 'account', 'LAYOUT', 'account_manage', '账号管理', 'ant-design:user-outlined', 0, null, 3, 4, 1, 0, 1, null, '/system/account/index', 1);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (5, '2022-08-06 14:14:21.836853', '2022-08-09 21:14:32.011644', 'index', '/system/account/index', 'get_all_users', '账号列表', null, 0, 'account_list', 4, 5, 1, 0, 1, '列表页，选一下呗', null, 1);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (6, '2022-08-06 14:14:21.866220', '2022-08-09 13:12:35.971888', null, null, 'user_add', '添加账号', null, 0, 'account_add', 4, 6, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (7, '2022-08-06 14:14:21.876627', '2022-08-09 13:12:35.947896', null, null, 'user_del', '删除账号', null, 0, 'account_delete', 4, 7, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (8, '2022-08-06 14:14:21.889291', '2022-08-09 13:12:35.884683', null, null, 'user_update', '修改账号', null, 0, 'account_update', 4, 8, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (9, '2022-08-06 14:14:21.855734', '2022-08-09 13:22:39.462782', null, null, 'get_user_by_id', '查看账号', null, 0, 'account_read', 4, 9, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (10, '2022-08-06 14:14:21.906665', '2022-08-09 13:12:36.020892', null, null, 'all_roles_options', '分配角色下拉框', null, 0, 'role_options', 4, 10, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (11, '2022-08-06 13:15:33.007310', '2022-08-09 13:12:36.004080', ':id', '/system/account/AccountDetail', 'account_detail', '账号详情页', null, 0, null, 4, 11, 1, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes, parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu) VALUES (12, '2022-08-07 08:15:32.937564', '2022-08-09 13:12:35.927920', 'role', 'LAYOUT', 'role_manage', '角色管理', 'ant-design:instagram-outlined', 0, null, 3, 12, 1, 0, 1, null, '/system/role/index', 1);

INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (13, '2022-08-06 14:14:21.960074', '2022-08-09 13:12:35.911153', 'index', '/system/role/index', 'get_all_role',
        '角色列表', null, 0, 'role_list', 12, 13, 1, 0, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (14, '2022-08-06 14:14:21.917957', '2022-08-09 13:12:35.900880', null, null, 'create_role', '角色添加', null, 0,
        'role_add', 12, 14, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (15, '2022-08-06 14:14:21.927614', '2022-08-09 13:12:35.868831', null, null, 'delete_role', '角色删除', null, 0,
        'role_delete', 12, 15, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (16, '2022-08-06 14:14:21.940821', '2022-08-09 13:12:35.957195', null, null, 'update_role', '角色修改', null, 0,
        'role_update', 12, 16, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (17, '2022-08-06 14:14:21.948251', '2022-08-09 13:12:35.996653', null, null, 'read_role', '查看角色', null, 0,
        'role_read', 12, 17, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (18, '2022-08-07 04:50:05.507380', '2022-08-09 13:12:35.893978', null, null, 'set_role_status', '角色状态', null,
        0, 'role_status', 12, 18, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (19, '2022-08-07 04:50:05.541618', '2022-08-09 13:12:35.964603', null, null, 'get_menu_tree', '获取菜单树', null,
        0, 'menu_tree', 12, 19, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (20, '2022-08-07 08:22:21.498551', '2022-08-09 13:12:36.012788', 'menu', 'LAYOUT', 'menu_manage', '菜单管理',
        'ant-design:appstore-filled', 0, null, 3, 20, 1, 0, 1, null, '/system/menu/index', 1);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (21, '2022-08-06 14:14:21.981029', '2022-08-09 21:21:10.844895', 'index', '/system/menu/index', 'get_all_access',
        '菜单列表', null, 0, 'menu_list', 20, 21, 1, 0, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (22, '2022-08-07 11:38:39.554280', '2022-08-09 13:12:35.861246', null, null, 'menu_update', '修改菜单', null, 0,
        'menu_update', 20, 22, 0, 1, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (23, '2022-08-09 13:25:27.839070', '2022-08-10 13:51:50.140489', '/about', 'LAYOUT', 'about_manage', '关于',
        'clarity:info-standard-line', 0, null, 0, 25, 1, 0, 1, null, '/about/index', 1);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (24, '2022-08-09 13:27:21.971149', '2022-08-10 13:51:50.126551', 'index', '/sys/about/index', 'about_index',
        '关于页面', null, 0, null, 23, 26, 1, 0, 1, null, null, 0);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (25, '2022-08-10 12:04:34.537043', '2022-08-10 13:51:50.151393', 'logs', 'LAYOUT', 'logs_manage', '系统日志',
        'clarity:flask-line', 0, null, 3, 23, 1, 0, 1, null, '/system/logs/index', 1);
INSERT INTO graduation.access (id, create_time, update_time, path, component, name, title, icon, is_button, scopes,
                            parent_id, order_no, is_router, hide_menu, status, remark, redirect, hide_children_in_menu)
VALUES (26, '2022-08-10 12:06:12.450458', '2022-08-10 13:51:50.112404', 'index', '/system/operation_logs/index',
        'logs_list', '日志列表', 'clarity:flask-line', 0, 'logs_list', 25, 24, 1, 1, 1, null, null, 1);


INSERT INTO graduation.access (create_time,update_time,`path`,component,name,title,icon,is_button,scopes,parent_id,order_no,is_router,hide_menu,status,remark,redirect,hide_children_in_menu) VALUES
	 ('2023-03-01 13:36:17.185029000','2023-03-01 07:40:17.556101000','/player','LAYOUT','proxy_manage','代理展示',NULL,0,NULL,0,27,1,0,1,NULL,'/player/index',1),
	 ('2023-03-01 13:47:42.050765000','2023-03-01 14:00:01.576738000','index','/system/player/index','player_view','播放界面',NULL,0,NULL,27,28,1,0,1,'',NULL,0),
	 ('2023-03-01 14:10:44.319853000','2023-03-01 06:13:58.310241000','/channel','LAYOUT','channel_manage','资源管理',NULL,0,NULL,0,30,1,0,1,NULL,'/channel/index',1),
	 ('2023-03-01 14:12:11.895845000','2023-03-01 06:17:44.587736000','index','/system/channel/index','channels_view','频道管理',NULL,0,NULL,33,31,1,0,1,NULL,NULL,0),
	 ('2023-03-01 14:15:54.225218000','2023-03-01 06:17:44.978514000','/monitor','LAYOUT','resource_manage','资源监控',NULL,0,NULL,0,33,1,0,1,NULL,'/monitor/index',1),
	 ('2023-03-01 14:16:51.477196000','2023-03-01 06:17:45.840785000','index','/system/monitor/index','monitor_view','性能监控',NULL,0,NULL,35,34,1,0,1,NULL,NULL,0);
