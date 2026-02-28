import React from 'react'
import { Tabs } from 'antd'
import {
    FileTextOutlined,
    FundOutlined,
    NotificationOutlined,
    PieChartOutlined,
    ShoppingOutlined,
    StockOutlined,
    SwapOutlined,
    TransactionOutlined,
} from '@ant-design/icons'

// Your page components
import Summary from '../Portfolio/Summary.tsx'
import Positions from "../Portfolio/Positions.tsx";
import Orders from "../Portfolio/Orders.tsx";
import Margins from "../Portfolio/Margins.tsx";
import Holdings from "../Portfolio/Holdings.tsx";
import Notifications from "../Portfolio/Notifications.tsx";
import Nifty from "../Portfolio/Nifty.tsx";
import Trade from '../Trade/Trade.tsx'
import MarketWatch from "../../MarketWatch/MarketWatch.tsx";


const { TabPane } = Tabs

const MainTabs: React.FC = () => {
    return (
        <Tabs
            defaultActiveKey="summary"
            tabPosition="top"
            type="line"
            items={[
                {
                    key: 'summary',
                    label: (
                        <>
                            <FileTextOutlined /> Summary
                        </>
                    ),
                    children: <Summary />,
                },
                {
                    key: 'positions',
                    label: (
                        <>
                            <FundOutlined /> Positions
                        </>
                    ),
                    children: <Positions />,
                },
                {
                    key: 'orders',
                    label: (
                        <>
                            <TransactionOutlined /> Orders
                        </>
                    ),
                    children: <Orders />,
                },
                {
                    key: 'margins',
                    label: (
                        <>
                            Margins
                        </>
                    ),
                    children: <Margins />,
                },
                {
                    key: 'holdings',
                    label: (
                        <>
                            <ShoppingOutlined /> Holdings
                        </>
                    ),
                    children: <Holdings />,
                },
                {
                    key: 'marketwatch',
                    label: (
                        <>
                            <PieChartOutlined /> Marketwatch
                        </>
                    ),
                    children: <MarketWatch />,
                },
                {
                    key: 'trade',
                    label: (
                        <>
                            <SwapOutlined /> Trade
                        </>
                    ),
                    children: <Trade />,
                },
                {
                    key: 'notifications',
                    label: (
                        <>
                            <NotificationOutlined /> Notifications
                        </>
                    ),
                    children: <Notifications />,
                },
                {
                    key: 'nifty',
                    label: (
                        <>
                            <PieChartOutlined /> Nifty
                        </>
                    ),
                    children: <Nifty />,
                },
            ]}
        />
    )
}

export default MainTabs
