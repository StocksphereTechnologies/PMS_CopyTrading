import React from "react";
import { Card, Row, Col, Divider } from "antd";

const OrdersSummaryCount: React.FC = () => {
  return (
    <Card style={{ marginTop: 24 }}>
        <h3 style={{ color: '#00b2b2', fontWeight: 'bold' }}>ORDERS SUMMARY [COUNT]</h3>
        <Row justify="space-between" gutter={[16, 16]}>
          <Divider />
          <Col xs={24} sm={12} md={6}>
            <div style={{ fontWeight: 'bold', color: '#0080ff' }}>» Open: 0 + 0 = <span style={{ color: '#0000ff' }}>0</span></div>
            <div style={{ fontWeight: 'bold', color: '#800080' }}>» Trig Pend: 0 + 0 = <span style={{ color: '#0000ff' }}>0</span></div>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div style={{ color: '#A52A2A', fontWeight: 'bold' }}>» Rejected: 0 + 0 = <span style={{ color: '#0000ff' }}>0</span></div>
            <div style={{ color: '#228B22', fontWeight: 'bold' }}>» Cancelled: 0 + 0 = <span style={{ color: '#0000ff' }}>0</span></div>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div style={{ color: '#006400', fontWeight: 'bold' }}>» Complete: 0 + 0 = <span style={{ color: '#0000ff' }}>0</span></div>
            <div style={{ color: '#00008B', fontWeight: 'bold' }}>» Unknown: 0 + 0 = <span style={{ color: '#0000ff' }}>0</span></div>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <div style={{ fontWeight: 'bold' }}>» Total: 0 + 0 = <span style={{ color: '#0000ff' }}>0</span></div>
            <div style={{ fontWeight: 'bold' }}>» Accounts = <span style={{ color: '#0000ff' }}>0</span></div>
          </Col>
        </Row>
    </Card>
  );
};

export default OrdersSummaryCount;
