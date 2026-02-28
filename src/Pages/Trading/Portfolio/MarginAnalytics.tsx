import React from 'react';
import { Row, Col, Typography, Card } from 'antd';
import {
    LockOutlined,
    ShoppingOutlined,
    TagOutlined,
    ClockCircleOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

const MarginsAnalytics = ({ updateTime = "09:40:49 PM" }) => {
    const metrics = [
        {
            label: 'Total',
            value: '₹0.46',
            icon: <ShoppingOutlined style={{ fontSize: 28, color: 'rgba(255, 255, 255, 0.6)' }} />,
            bgColor: 'linear-gradient(to right, #00c9ff, #00e5e5)',
        },
        {
            label: 'Utilized',
            value: '₹0.00',
            icon: <LockOutlined style={{ fontSize: 28, color: 'rgba(255, 255, 255, 0.6)' }} />,
            bgColor: '#ffa07a',
        },
        {
            label: 'Available',
            value: '₹0.46',
            icon: <TagOutlined style={{ fontSize: 28, color: 'rgba(255, 255, 255, 0.6)' }} />,
            bgColor: 'linear-gradient(to right, #00e676, #00c853)',
        },
    ];

    return (
        <div>
            <Card style={{ margin: 24, borderRadius: 12 }}>
                <Title level={5} style={{ marginBottom: 24, color: '#00b39f' }}>
                    Margins Analytics
                </Title>

                <Row gutter={[16, 16]} align="middle" wrap>
                    {metrics.map((item) => (
                        <Col key={item.label}>
                            <Card
                                style={{
                                    background: item.bgColor,
                                    borderRadius: 12,
                                    width: 200,
                                    height: 100,
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '16px 20px',
                                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                                }}
                                bodyStyle={{ padding: 0 }}
                            >
                                <div>
                                    <Text strong style={{ color: 'white', fontSize: 14 }}>{item.label}</Text>
                                    <div style={{ fontSize: 20, color: 'white' }}>{item.value}</div>
                                </div>
                                {item.icon}
                            </Card>
                        </Col>
                    ))}

                    <Col>
                        <Card
                            style={{
                                background: '#ffeef0',
                                borderRadius: 12,
                                padding: '16px 20px',
                                minWidth: 220,
                                height: 100,
                                display: 'flex',
                                alignItems: 'center',
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

export default MarginsAnalytics;
