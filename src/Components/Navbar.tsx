import React from 'react'
import { Menu } from 'antd'
import { Link } from 'react-router-dom'
import {
    SettingOutlined,
    UserOutlined,
    AppstoreOutlined,
    QuestionCircleOutlined,
    StockOutlined
} from '@ant-design/icons'
import { FundOutlined } from '@ant-design/icons';

const { SubMenu } = Menu

const Navbar: React.FC = () => {
    const items = [
        {
            key: 'autotrader',
            icon: <AppstoreOutlined />,
            label: 'AutoTrader',
            children: [
                {
                    key: 'activity',
                    label: <Link to="/autotrader/activity">Activity</Link>,
                },
                {
                    key: 'instruments',
                    label: <Link to="/autotrader/instruments">Instruments</Link>,
                },
            ],
        },
        {
            key: 'trading',
            icon: <StockOutlined />,
            label: 'Trading',
            children: [
                {
                    key: 'portfolio',
                    label: <Link to="/trading/portfolio">Portfolio</Link>,
                },
            ],
        },
        {
            key: 'settings',
            icon: <SettingOutlined />,
            label: 'Settings',
            children: [
                {
                    key: 'general',
                    label: <Link to="/settings/general">General</Link>,
                },
                {
                    key: 'tradingaccounts',
                    label: <Link to="/settings/tradingaccounts">Trading Accounts</Link>,
                },
                {
                    key: 'pseudoaccounts',
                    label: <Link to="/settings/pseudoaccounts">Pseudo Accounts</Link>,
                },
                {
                    key: 'groupaccounts',
                    label: <Link to="/settings/groupaccounts">Group Accounts</Link>,
                },
                {
                    key: 'masteraccounts',
                    label: <Link to="/settings/masteraccounts">Master Accounts</Link>,
                },
                {
                    key: 'security',
                    label: <Link to="/settings/security">Security</Link>,
                },
            ],
        },
        {
            key: 'help',
            icon: <QuestionCircleOutlined />,
            label: <Link to="/help">Help</Link>,
        },
        {
            key: 'user-menu',
            icon: <UserOutlined />,
            label: 'User',
            children: [
                {
                    key: 'user-account',
                    label: <Link to="/user/account">Account</Link>,
                },
                {
                    key: 'profile',
                    label: <Link to="/user/profile">Profile</Link>,
                },
                {
                    key: 'logout',
                    label: <Link to="/user/logout">Logout</Link>,
                },
            ],
        },
        {
            key: 'screener-menu',
            icon: <FundOutlined />,
            label: 'Screener',
            children: [
                {
                    key: 'screener-view',
                    label: <Link to="/screener/screener">Screener</Link>,
                },
            ],
        },
    ];

    return (
        <Menu
            mode="horizontal"
            theme="dark"
            style={{ display: 'flex', justifyContent: 'flex-start' }}
            items={items}
        />
    );
}

export default Navbar
