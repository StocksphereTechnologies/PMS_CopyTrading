import React from 'react';
import { Row, Col, Typography, Card } from 'antd';
import StatCard from '../../../Components/StatsCards.tsx';

const { Title, Text } = Typography;
const PositionAnalyticsSummary = (props: { title: any; }) => {
    const { title } = props
    return (<div>
        <Card style={{ margin: 24, borderRadius: 12 }}>
            <Title level={5} style={{ marginBottom: 24, color: '#00bcd4' }}>
                {title}
            </Title>

            <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8}>
                    <StatCard label="M2M" value="0.00" icon={''} />
                </Col>
                <Col xs={24} sm={12} md={8}>
                    <StatCard label="PnL" value="0.00" icon={''} />
                </Col>
                <Col xs={24} sm={12} md={8}>
                    <StatCard label="AT PnL" value="0.00" icon={''} />
                </Col>

                <Col xs={24} sm={12} md={8}>
                    <Card style={{ background: 'linear-gradient(to right, #00c9ff, #92fe9d)', borderRadius: 12 }}>
                        <Text style={{ color: 'white' }}>Total</Text>
                        <Title level={3} style={{ color: 'white' }}>0</Title>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text style={{ color: 'white' }}>Open 0</Text>
                            <Text style={{ color: 'white' }}>Closed 0</Text>
                        </div>
                    </Card>
                </Col>

                <Col xs={24} sm={12} md={8}>
                    <Card style={{ background: '#ffe6e6', borderRadius: 12 }}>
                        <Text style={{ color: '#f44336', fontWeight: 500 }}>
                            🔒 Update Time <span style={{ color: '#555' }}>11:13:46 PM</span>
                        </Text>
                    </Card>
                </Col>
            </Row>
        </Card>
    </div>)
}
export default PositionAnalyticsSummary
