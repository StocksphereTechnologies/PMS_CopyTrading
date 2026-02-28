import React, { useEffect, useState } from 'react';
import SmartTable from '../../../Components/Table.tsx';
import type { ColumnsType } from 'antd/es/table';
import { httpClient } from '../../../Services/apiService.ts';

const symbolLevelColumns: ColumnsType<any> = [
    {
        title: 'Position [NET]',
        children: [
            {
                title: 'Exchange',
                dataIndex: 'exchange',
                key: 'exchange',
            },
            {
                title: 'Symbol',
                dataIndex: 'symbol',
                key: 'symbol',
            },
            {
                title: 'Buy Qty',
                dataIndex: 'buyQty',
                key: 'buyQty',
            },
            {
                title: 'Sell Qty',
                dataIndex: 'sellQty',
                key: 'sellQty',
            },
            {
                title: 'Net Qty',
                dataIndex: 'netQty',
                key: 'netQty',
            },
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
                title: 'Buy Val',
                dataIndex: 'buyVal',
                key: 'buyVal',
            },
            {
                title: 'Sell Val',
                dataIndex: 'sellVal',
                key: 'sellVal',
            },
            {
                title: 'Net Val',
                dataIndex: 'netVal',
                key: 'netVal',
            },
            {
                title: 'Buy Avg',
                dataIndex: 'buyAvg',
                key: 'buyAvg',
            },
            {
                title: 'Sell Avg',
                dataIndex: 'sellAvg',
                key: 'sellAvg',
            },
        ],
    },
    {
        title: 'Holdings',
        children: [
            {
                title: 'Exchange',
                dataIndex: 'holdingExchange',
                key: 'holdingExchange',
            },
            {
                title: 'Symbol',
                dataIndex: 'holdingSymbol',
                key: 'holdingSymbol',
            },
        ],
    },
];



const symbolLevelDataSource = [
    {
        key: '1',
        exchange: '',
        symbol: '',
        buyQty: 0,
        sellQty: 0,
        netQty: 0,
        m2m: '₹0.00',
        pnl: '₹0.00',
        atPnl: '₹0.00',
        buyVal: '₹0.00',
        sellVal: '₹0.00',
        netVal: '₹0.00',
        buyAvg: '₹0.00',
        sellAvg: '₹0.00',
        holdingExchange: '',
        holdingSymbol: '',
    },
];


const SymbolLevelSummary: React.FC = () => {
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
            title="Account Level Summary"
            columns={symbolLevelColumns}
            dataSource={symbolLevelDataSource}
        />
    );
};

export default SymbolLevelSummary;
