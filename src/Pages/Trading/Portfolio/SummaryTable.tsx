import React, { useEffect, useState } from 'react';
import SmartTable from '../../../Components/Table.tsx';
import type { ColumnsType } from 'antd/es/table';

const columns: ColumnsType<any> = [
    {
        title: 'Account',
        children: [
            {
                title: 'Pseudo Acc',
                dataIndex: 'pseudoAcc',
                key: 'pseudoAcc',
                sorter: (a: any, b: any) =>
                    String(a.pseudoAcc).localeCompare(String(b.pseudoAcc)),
            },
            {
                title: 'Trading Acc',
                dataIndex: 'tradingAcc',
                key: 'tradingAcc',
                sorter: (a: any, b: any) =>
                    String(a.tradingAcc).localeCompare(String(b.tradingAcc)),
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
                title: '#Total',
                dataIndex: 'totalPos',
                key: 'totalPos',
                sorter: (a: any, b: any) => Number(a.totalPos) - Number(b.totalPos),
            },
            {
                title: '#Open',
                dataIndex: 'openPos',
                key: 'openPos',
                sorter: (a: any, b: any) => Number(a.openPos) - Number(b.openPos),
            },
            {
                title: '#Closed',
                dataIndex: 'closedPos',
                key: 'closedPos',
                sorter: (a: any, b: any) => Number(a.closedPos) - Number(b.closedPos),
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
                sorter: (a: any, b: any) => Number(a.marginTotal) - Number(b.marginTotal),
            },
            {
                title: 'Utilized',
                dataIndex: 'marginUtilized',
                key: 'marginUtilized',
                sorter: (a: any, b: any) =>
                    Number(a.marginUtilized) - Number(b.marginUtilized),
            },
            {
                title: 'Available',
                dataIndex: 'marginAvailable',
                key: 'marginAvailable',
                sorter: (a: any, b: any) =>
                    Number(a.marginAvailable) - Number(b.marginAvailable),
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
                render: (v: any) => (v === undefined || v === null ? 0 : v),
                sorter: (a: any, b: any) => (a.orderTotal || 0) - (b.orderTotal || 0),
            },
            {
                title: '#Open',
                dataIndex: 'orderOpen',
                key: 'orderOpen',
                render: (v: any) => (v === undefined || v === null ? 0 : v),
                sorter: (a: any, b: any) => (a.orderOpen || 0) - (b.orderOpen || 0),
            },
            {
                title: '#T-Pend',
                dataIndex: 'orderTPend',
                key: 'orderTPend',
                render: (v: any) => (v === undefined || v === null ? 0 : v),
                sorter: (a: any, b: any) => (a.orderTPend || 0) - (b.orderTPend || 0),
            },
            {
                title: '#Complete',
                dataIndex: 'orderComplete',
                key: 'orderComplete',
                render: (v: any) => (v === undefined || v === null ? 0 : v),
                sorter: (a: any, b: any) => (a.orderComplete || 0) - (b.orderComplete || 0),
            },
            {
                title: '#Rejected',
                dataIndex: 'orderRejected',
                key: 'orderRejected',
                render: (v: any) => (v === undefined || v === null ? 0 : v),
                sorter: (a: any, b: any) => (a.orderRejected || 0) - (b.orderRejected || 0),
            },
            {
                title: '#Cancelled',
                dataIndex: 'orderCancelled',
                key: 'orderCancelled',
                render: (v: any) => (v === undefined || v === null ? 0 : v),
                sorter: (a: any, b: any) => (a.orderCancelled || 0) - (b.orderCancelled || 0),
            }
        ]
    },
    {
        title: 'Holdings',
        children: [
            {
                title: '#Count',
                dataIndex: 'holdingCount',
                key: 'holdingCount',
                sorter: (a: any, b: any) =>
                    Number(a.holdingCount) - Number(b.holdingCount),
            },
            {
                title: 'PnL',
                dataIndex: 'holdingPnl',
                key: 'holdingPnl',
                sorter: (a: any, b: any) =>
                    Number(a.holdingPnl) - Number(b.holdingPnl),
            },
            {
                title: 'Curr Val',
                dataIndex: 'currVal',
                key: 'currVal',
                sorter: (a: any, b: any) =>
                    Number(a.currVal) - Number(b.currVal),
            },
            {
                title: 'Total Qty',
                dataIndex: 'holdingTotalQty',
                key: 'holdingTotalQty',
                sorter: (a: any, b: any) =>
                    Number(a.holdingTotalQty) - Number(b.holdingTotalQty),
            },
            {
                title: 'Quantity',
                dataIndex: 'holdingQty',
                key: 'holdingQty',
                sorter: (a: any, b: any) =>
                    Number(a.holdingQty) - Number(b.holdingQty),
            },
            {
                title: 'T1 Qty',
                dataIndex: 'holdingT1Qty',
                key: 'holdingT1Qty',
                sorter: (a: any, b: any) =>
                    Number(a.holdingT1Qty) - Number(b.holdingT1Qty),
            },
        ],
    },

    {
        title: 'Position [DAY]',
        children: [
            {
                title: 'M2M',
                dataIndex: 'dayM2M',
                key: 'dayM2M',
                sorter: (a: any, b: any) =>
                    Number(a.dayM2M) - Number(b.dayM2M),
            },
            {
                title: 'PnL',
                dataIndex: 'dayPnl',
                key: 'dayPnl',
                sorter: (a: any, b: any) =>
                    Number(a.dayPnl) - Number(b.dayPnl),
            },
            {
                title: 'AT PnL',
                dataIndex: 'dayATPnl',
                key: 'dayATPnl',
                sorter: (a: any, b: any) =>
                    Number(a.dayATPnl) - Number(b.dayATPnl),
            },
            {
                title: '#Total',
                dataIndex: 'dayTotal',
                key: 'dayTotal',
                sorter: (a: any, b: any) =>
                    Number(a.dayTotal) - Number(b.dayTotal),
            },
            {
                title: '#Open',
                dataIndex: 'dayOpen',
                key: 'dayOpen',
                sorter: (a: any, b: any) =>
                    Number(a.dayOpen) - Number(b.dayOpen),
            },
            {
                title: '#Closed',
                dataIndex: 'dayClosed',
                key: 'dayClosed',
                sorter: (a: any, b: any) =>
                    Number(a.dayClosed) - Number(b.dayClosed),
            },
        ],
    },
];

interface Props {
    data: any[]
}

const SummaryTable: React.FC<Props> = ({ data }) => {

    return (
        <SmartTable
            exportButtons
            title="Account Level Summary"
            columns={columns}
            dataSource={data}
        />
    )
}

export default SummaryTable;
