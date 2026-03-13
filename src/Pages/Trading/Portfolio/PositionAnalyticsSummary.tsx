import React from 'react'
import { Row, Col, Typography, Card } from 'antd'
import StatCard from '../../../Components/StatsCards.tsx'

const { Title, Text } = Typography

interface PositionAnalyticsData {
    m2m: number
    pnl: number
    atPnl: number
    total: number
    open: number
    closed: number
}

interface Props {
    title: string
    data: PositionAnalyticsData
    updateTime?: string
}

const PositionAnalyticsSummary: React.FC<Props> = ({ title, data, updateTime }) => {
    return (
        <div>
            <Card style={{ margin: 24, borderRadius: 12 }}>

                <Title level={5} style={{ marginBottom: 24, color: '#00bcd4' }}>
                    {title}
                </Title>

                <Row gutter={[16, 16]}>

                    <Col xs={24} sm={12} md={8}>
                        <StatCard label="M2M" value={data.m2m} />
                    </Col>

                    <Col xs={24} sm={12} md={8}>
                        <StatCard label="PnL" value={data.pnl} />
                    </Col>

                    <Col xs={24} sm={12} md={8}>
                        <StatCard label="AT PnL" value={data.atPnl} />
                    </Col>

                    <Col xs={24} sm={12} md={8}>
                        <Card style={{ background: 'linear-gradient(to right,#00c9ff,#92fe9d)', borderRadius: 12 }}>
                            <Text style={{ color: 'white' }}>Total</Text>

                            <Title level={3} style={{ color: 'white' }}>
                                {data.total}
                            </Title>

                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Text style={{ color: 'white' }}>Open {data.open}</Text>
                                <Text style={{ color: 'white' }}>Closed {data.closed}</Text>
                            </div>

                        </Card>
                    </Col>

                </Row>
                <Row style={{ marginTop: 16 }}>
                    <Col>
                        <Card
                            style={{
                                background: '#ffeef0',
                                borderRadius: 12,
                                padding: '12px 20px',
                                minWidth: 220,
                            }}
                            bodyStyle={{ padding: 0 }}
                        >
                            <Text style={{ fontWeight: 500, color: '#00b39f', fontSize: 14 }}>
                                Update Time <span style={{ color: '#555', fontWeight: 600 }}>{updateTime}</span>
                            </Text>
                        </Card>
                    </Col>
                </Row>

            </Card>
        </div>
    )
}

export default PositionAnalyticsSummary