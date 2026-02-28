import React, { useEffect, useState } from 'react';
import SmartTable from '../../../Components/Table.tsx';
import type { ColumnsType } from 'antd/es/table';
import { httpClient } from '../../../Services/apiService.ts';

const columns: ColumnsType<any> = [
    {
        title: 'Account',
        children: [
            {
                title: 'Pseudo Acc',
                dataIndex: 'pseudoAcc',
                key: 'pseudoAcc',
            },
            {
                title: 'Trading Acc',
                dataIndex: 'tradingAcc',
                key: 'tradingAcc',
            },
        ],
    },
    {
        title: 'Position [NET]',
        children: [
            {
                title: 'M2M',
                dataIndex: 'm2m',
                key: 'm2m',
            },
            {
                title: 'PnL',
                dataIndex: 'pnl',
                key: 'pnl',
            },
            {
                title: 'AT PnL',
                dataIndex: 'atPnl',
                key: 'atPnl',
            },
            {
                title: '#Total',
                dataIndex: 'totalPos',
                key: 'totalPos',
            },
            {
                title: '#Open',
                dataIndex: 'openPos',
                key: 'openPos',
            },
            {
                title: '#Closed',
                dataIndex: 'closedPos',
                key: 'closedPos',
            },
        ],
    },
    {
        title: 'Margin',
        children: [
            {
                title: 'Total',
                dataIndex: 'marginTotal',
                key: 'marginTotal',
            },
            {
                title: 'Utilized',
                dataIndex: 'marginUtilized',
                key: 'marginUtilized',
            },
            {
                title: 'Available',
                dataIndex: 'marginAvailable',
                key: 'marginAvailable',
            },
        ],
    },
    {
        title: 'Orders',
        children: [
            {
                title: '#Total',
                dataIndex: 'orderTotal',
                key: 'orderTotal',
            },
            {
                title: '#Open',
                dataIndex: 'orderOpen',
                key: 'orderOpen',
            },
            {
                title: '#T-Pend',
                dataIndex: 'orderTPend',
                key: 'orderTPend',
            },
        ],
    },
];


const data = [
    {
        key: '1',
        pseudoAcc: '53135052',
        tradingAcc: '53135052',
        m2m: '₹0.00',
        pnl: '₹0.00',
        atPnl: '₹0.00',
        totalPos: 0,
        openPos: 0,
        closedPos: 0,
        marginTotal: '₹0.46',
        marginUsed: '₹0.00',
        marginAvailable: '₹0.46',
        ordersTotal: 0,
        ordersOpen: 0,
        ordersTPend: 0,
        ordersCompleted: 0,
    },
];

const SummaryTable: React.FC = () => {
    // const [accSummary, setAccSummary] = useState([])
    // useEffect(() => {
    //     const fetchAccSummary = async () => {
    //         try {
    //             const data = await httpClient('/api/trading/portfolioSummary', {
    //                 method: 'GET',
    //                 params: {
    //                     pseudoAccount: '53135052',
    //                 },
    //                 headers: {
    //                     'api-key': 'f0a63155-883b-4fb5-b73f-8fefe03f4e4d',
    //                 },
    //             });
    //             setAccSummary(data)
    //             console.log('API Data:', data);
    //         } catch (err) {
    //             console.error('Error:', err);
    //         }
    //     };
    //     fetchAccSummary()
    // }, [])
    return (

        <SmartTable
            exportButtons
            title="Symbol Level Summary"
            columns={columns}
            dataSource={data}
        />
    );
};

export default SummaryTable;
