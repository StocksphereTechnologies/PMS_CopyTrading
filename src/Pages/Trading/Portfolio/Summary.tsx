import React from 'react';
import { Row, Col, Typography, Card } from 'antd';
import StatCard from '../../../Components/StatsCards.tsx';
import SummaryTable from './SummaryTable.tsx';
import PositionAnalyticsSummary from './PositionAnalyticsSummary.tsx';
import SymbolLevelSummary from './SymbolLevelSummary.tsx';
import OrdersAnalyticsSummary from './OrderAnalytics.tsx';
import MarginsAnalytics from './MarginAnalytics.tsx';
// import { Icon } from '@iconify/react';

const { Title, Text } = Typography;
const Summary = () => {
    return (<div>
        <SummaryTable />
        <SymbolLevelSummary />
        <PositionAnalyticsSummary title='Positions Analytics [NET]' />
        <PositionAnalyticsSummary title='Positions Analytics [Day]' />
        <OrdersAnalyticsSummary />
        <MarginsAnalytics />

    </div>)
}
export default Summary
