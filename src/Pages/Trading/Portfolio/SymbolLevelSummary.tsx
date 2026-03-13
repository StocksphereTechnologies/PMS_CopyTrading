import React, { useEffect, useState } from 'react';
import SmartTable from '../../../Components/Table.tsx';
import type { ColumnsType } from 'antd/es/table';

const symbolLevelColumns: ColumnsType<any> = [
    {
        title: 'Position [NET]',
        children: [
            {
                title: 'Exchange',
                dataIndex: 'exchange',
                key: 'exchange',
                sorter: (a: any, b: any) =>
                    String(a.exchange).localeCompare(String(b.exchange)),
            },
            {
                title: 'Symbol',
                dataIndex: 'symbol',
                key: 'symbol',
                sorter: (a: any, b: any) =>
                    String(a.symbol).localeCompare(String(b.symbol)),
            },
            {
                title: 'Buy Qty',
                dataIndex: 'buyQty',
                key: 'buyQty',
                sorter: (a: any, b: any) => Number(a.buyQty) - Number(b.buyQty),
            },
            {
                title: 'Sell Qty',
                dataIndex: 'sellQty',
                key: 'sellQty',
                sorter: (a: any, b: any) => Number(a.sellQty) - Number(b.sellQty),
            },
            {
                title: 'Net Qty',
                dataIndex: 'netQty',
                key: 'netQty',
                sorter: (a: any, b: any) => Number(a.netQty) - Number(b.netQty),
            },
            {
                title: 'M2M',
                dataIndex: 'm2m',
                key: 'm2m',
                sorter: (a: any, b: any) => Number(a.m2m) - Number(b.m2m),
            },
            {
                title: 'PnL',
                dataIndex: 'pnl',
                key: 'pnl',
                sorter: (a: any, b: any) => Number(a.pnl) - Number(b.pnl),
            },
            {
                title: 'AT PnL',
                dataIndex: 'atPnl',
                key: 'atPnl',
                sorter: (a: any, b: any) => Number(a.atPnl) - Number(b.atPnl),
            },
            {
                title: 'Buy Val',
                dataIndex: 'buyVal',
                key: 'buyVal',
                sorter: (a: any, b: any) => Number(a.buyVal) - Number(b.buyVal),
            },
            {
                title: 'Sell Val',
                dataIndex: 'sellVal',
                key: 'sellVal',
                sorter: (a: any, b: any) => Number(a.sellVal) - Number(b.sellVal),
            },
            {
                title: 'Net Val',
                dataIndex: 'netVal',
                key: 'netVal',
                sorter: (a: any, b: any) => Number(a.netVal) - Number(b.netVal),
            },
            {
                title: 'Buy Avg',
                dataIndex: 'buyAvg',
                key: 'buyAvg',
                sorter: (a: any, b: any) => Number(a.buyAvg) - Number(b.buyAvg),
            },
            {
                title: 'Sell Avg',
                dataIndex: 'sellAvg',
                key: 'sellAvg',
                sorter: (a: any, b: any) => Number(a.sellAvg) - Number(b.sellAvg),
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
                sorter: (a: any, b: any) =>
                    String(a.holdingExchange).localeCompare(String(b.holdingExchange)),
            },
            {
                title: 'Symbol',
                dataIndex: 'holdingSymbol',
                key: 'holdingSymbol',
                sorter: (a: any, b: any) =>
                    String(a.holdingSymbol).localeCompare(String(b.holdingSymbol)),
            },
            {
                title: 'Pnl',
                dataIndex: 'holdingPnl',
                key: 'holdingPnl',
                sorter: (a: any, b: any) => Number(a.holdingPnl) - Number(b.holdingPnl),
            },
            {
                title: 'Curr Val',
                dataIndex: 'holdingCurrVal',
                key: 'holdingCurrVal',
                sorter: (a: any, b: any) => Number(a.holdingCurrVal) - Number(b.holdingCurrVal),
            },
            {
                title: 'Total Qty',
                dataIndex: 'holdingTotalQty',
                key: 'holdingTotalQty',
                sorter: (a: any, b: any) => Number(a.holdingTotalQty) - Number(b.holdingTotalQty),
            },
            {
                title: 'Quantity',
                dataIndex: 'holdingQty',
                key: 'holdingQty',
                sorter: (a: any, b: any) => Number(a.holdingQty) - Number(b.holdingQty),
            },
            {
                title: 'T1 Qty',
                dataIndex: 'holdingT1Qty',
                key: 'holdingT1Qty',
                sorter: (a: any, b: any) => Number(a.holdingT1Qty) - Number(b.holdingT1Qty),
            }
        ],
    },
    {
        title: 'Position [DAY]',
        children: [
            {
                title: 'Quantity',
                dataIndex: 'dayQty',
                key: 'dayQty',
                sorter: (a: any, b: any) => Number(a.dayQty) - Number(b.dayQty),
            },
            {
                title: 'T1 Qty',
                dataIndex: 'dayT1Qty',
                key: 'dayT1Qty',
                sorter: (a: any, b: any) => Number(a.dayT1Qty) - Number(b.dayT1Qty),
            },
            {
                title: 'Exchange',
                dataIndex: 'dayExchange',
                key: 'dayExchange',
                sorter: (a: any, b: any) =>
                    String(a.dayExchange).localeCompare(String(b.dayExchange)),
            },
            {
                title: 'Symbol',
                dataIndex: 'daySymbol',
                key: 'daySymbol',
                sorter: (a: any, b: any) =>
                    String(a.daySymbol).localeCompare(String(b.daySymbol)),
            },
            {
                title: 'Buy Qty',
                dataIndex: 'dayBuyQty',
                key: 'dayBuyQty',
                sorter: (a: any, b: any) => Number(a.dayBuyQty) - Number(b.dayBuyQty),
            },
            {
                title: 'Sell Qty',
                dataIndex: 'daySellQty',
                key: 'daySellQty',
                sorter: (a: any, b: any) => Number(a.daySellQty) - Number(b.daySellQty),
            },
            {
                title: 'Net Qty',
                dataIndex: 'dayNetQty',
                key: 'dayNetQty',
                sorter: (a: any, b: any) => Number(a.dayNetQty) - Number(b.dayNetQty),
            },
            {
                title: 'M2M',
                dataIndex: 'dayM2m',
                key: 'dayM2m',
                sorter: (a: any, b: any) => Number(a.dayM2m) - Number(b.dayM2m),
            },
            {
                title: 'PnL',
                dataIndex: 'dayPnl',
                key: 'dayPnl',
                sorter: (a: any, b: any) => Number(a.dayPnl) - Number(b.dayPnl),
            },
            {
                title: 'AT PnL',
                dataIndex: 'dayAtPnl',
                key: 'dayAtPnl',
                sorter: (a: any, b: any) => Number(a.dayAtPnl) - Number(b.dayAtPnl),
            },
            {
                title: 'Buy Val',
                dataIndex: 'dayBuyVal',
                key: 'dayBuyVal',
                sorter: (a: any, b: any) => Number(a.dayBuyVal) - Number(b.dayBuyVal),
            },
            {
                title: 'Sell Val',
                dataIndex: 'daySellVal',
                key: 'daySellVal',
                sorter: (a: any, b: any) => Number(a.daySellVal) - Number(b.daySellVal),
            },
            {
                title: 'Net Val',
                dataIndex: 'dayNetVal',
                key: 'dayNetVal',
                sorter: (a: any, b: any) => Number(a.dayNetVal) - Number(b.dayNetVal),
            },
            {
                title: 'Buy Avg',
                dataIndex: 'dayBuyAvg',
                key: 'dayBuyAvg',
                sorter: (a: any, b: any) => Number(a.dayBuyAvg) - Number(b.dayBuyAvg),
            },
            {
                title: 'Sell Avg',
                dataIndex: 'daySellAvg',
                key: 'daySellAvg',
                sorter: (a: any, b: any) => Number(a.daySellAvg) - Number(b.daySellAvg),
            },
        ],
    }
];

interface Props {
    data: any[]
}

const SymbolLevelSummary: React.FC<Props> = ({ data }) => {

    return (
        <SmartTable
            exportButtons
            title="Symbol Level Summary"
            columns={symbolLevelColumns}
            dataSource={data}
        />
    )
}

export default SymbolLevelSummary;
