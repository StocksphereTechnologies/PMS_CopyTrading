import React from 'react';
import SmartTable from '../../Components/Table'; // Adjust import path if needed
import { Button } from 'antd';

const columns = [
    {
        title: 'Symbol',
        dataIndex: 'symbol',
        key: 'symbol',
        fixed: 'left',
        width: 220,
    },
    {
        title: 'Ltp',
        dataIndex: 'ltp',
        key: 'ltp',
        width: 100,
        render: (value: string) => (
            <div style={{ background: '#fffbe6', textAlign: 'center' }}>{value}</div>
        ),
    },
    {
        title: 'Buy',
        key: 'buy',
        width: 80,
        render: () => (
            <Button type="primary" size="small" style={{ background: '#52c41a' }}>
                Buy
            </Button>
        ),
    },
    {
        title: 'Sell',
        key: 'sell',
        width: 80,
        render: () => (
            <Button type="primary" danger size="small">
                Sell
            </Button>
        ),
    },
    {
        title: '% Chg',
        dataIndex: 'percentChange',
        key: 'percentChange',
        width: 100,
        render: (value: number) => (
            <span style={{ color: value >= 0 ? 'green' : 'red' }}>{value}%</span>
        ),
    },
    {
        title: 'Time',
        dataIndex: 'time',
        key: 'time',
        width: 150,
    },
    {
        title: 'Volume',
        dataIndex: 'volume',
        key: 'volume',
        width: 100,
    },
    {
        title: 'OI',
        dataIndex: 'oi',
        key: 'oi',
        width: 100,
    },
    {
        title: 'Open',
        dataIndex: 'open',
        key: 'open',
        width: 100,
    },
    {
        title: 'High',
        dataIndex: 'high',
        key: 'high',
        width: 100,
    },
    {
        title: 'Low',
        dataIndex: 'low',
        key: 'low',
        width: 100,
    },
    {
        title: 'Prev. Cl',
        dataIndex: 'prevClose',
        key: 'prevClose',
        width: 100,
    },
    {
        title: 'Avg. Prc',
        dataIndex: 'avgPrice',
        key: 'avgPrice',
        width: 100,
    },
    {
        title: 'Ltq.',
        dataIndex: 'ltq',
        key: 'ltq',
        width: 100,
    },
    {
        title: 'Tot. B-Qty',
        dataIndex: 'totalBuyQty',
        key: 'totalBuyQty',
        width: 100,
    },
    {
        title: 'Tot. S-Qty',
        dataIndex: 'totalSellQty',
        key: 'totalSellQty',
        width: 100,
    },
];

const data = [
    {
        key: '1',
        symbol: 'NIFTY_10-JUL-2025_CE_22300',
        ltp: '102.45',
        percentChange: 1.25,
        time: '11:20:45',
        volume: '10,200',
        oi: '5,600',
        open: '100.00',
        high: '105.00',
        low: '98.50',
        prevClose: '101.00',
        avgPrice: '102.00',
        ltq: '250',
        totalBuyQty: '6,500',
        totalSellQty: '5,300',
    },
];

const MarketWatch: React.FC = () => {
    return (
        <SmartTable
            title="Market Watch"
            columns={columns}
            dataSource={data}
            rowKey="key"
            searchable
        />
    );
};

export default MarketWatch;
