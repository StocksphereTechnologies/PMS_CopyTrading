import React from 'react';
import { Row, Col, Typography, Card } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const OrdersAnalyticsSummary = ({ title = "Orders Analytics", updateTime = "09:40:47 PM" }) => {
    const statItems = [
        { label: 'Total', value: 0 },
        { label: 'Open', value: 0 },
        { label: 'Complete', value: 0 },
        { label: 'Trig-Pend', value: 0 },
        { label: 'Cancelled', value: 0 },
        { label: 'Rejected', value: 0 },
    ];

    return (
        <div>
            <Card style={{ margin: 24, borderRadius: 12 }}>
                <Title level={5} style={{ marginBottom: 24, color: '#00b39f' }}>
                    {title}
                </Title>

                <Row gutter={[16, 16]} align="middle">
                    <Col flex="auto">
                        <Card
                            style={{
                                background: 'linear-gradient(to right, #00c9ff, #00e5e5)',
                                borderRadius: 12,
                                padding: '16px 20px',
                            }}
                            bodyStyle={{ padding: 0 }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap' }}>
                                {statItems.map((item) => (
                                    <div
                                        key={item.label}
                                        style={{
                                            textAlign: 'center',
                                            color: 'white',
                                            minWidth: 80,
                                            margin: '8px 12px',
                                        }}
                                    >
                                        <Text strong style={{ fontSize: 14 }}>{item.label}</Text>
                                        <div style={{ fontSize: 20 }}>{item.value}</div>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    </Col>

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
                                <ClockCircleOutlined style={{ marginRight: 6, color: '#f44336' }} />
                                Update Time <span style={{ color: '#555', fontWeight: 600 }}>{updateTime}</span>
                            </Text>
                        </Card>
                    </Col>
                </Row>
            </Card>
        </div>
    );
};

export default OrdersAnalyticsSummary;
