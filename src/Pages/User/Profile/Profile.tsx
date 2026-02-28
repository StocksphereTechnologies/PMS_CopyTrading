import React from 'react';
import { Card, Form, Input, Button, Row, Col, Typography, message } from 'antd';

const { Title } = Typography;

const Profile = () => {
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('Submitted:', values);
    localStorage.setItem('userProfile', JSON.stringify(values));
    message.success('Profile saved successfully!');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f5f7fa',
        padding: '4rem 1rem',
        fontFamily: "'Segoe UI', sans-serif",
      }}
    >
      <Card
        style={{
          maxWidth: 950,
          margin: '0 auto',
          padding: '2.5rem 3rem',
          borderRadius: '20px',
          backgroundColor: '#ffffff',
          boxShadow: '0 10px 35px rgba(0, 0, 0, 0.07)',
        }}
      >
        <Title
          level={2}
          style={{
            textAlign: 'center',
            color: '#0d1b2a', // New title color
            fontWeight: 700,
            marginBottom: '2.5rem',
            fontSize: '28px',
          }}
        >
          Profile
        </Title>

        <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{}}>
          <Row gutter={[24, 16]}>
            <Col span={12}>
              <Form.Item
                label={<span style={{ fontWeight: 600, fontSize: 15 }}>Full Name</span>}
                name="fullName"
                rules={[{ required: true, message: 'Please enter your full name' }]}
              >
                <Input
                  placeholder="John Doe"
                  style={{ borderRadius: 10, height: 46, fontSize: 15 }}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label={<span style={{ fontWeight: 600, fontSize: 15 }}>Email</span>}
                name="email"
                rules={[{ required: true, message: 'Please enter your email' }]}
              >
                <Input
                  type="email"
                  placeholder="john@example.com"
                  style={{ borderRadius: 10, height: 46, fontSize: 15 }}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label={<span style={{ fontWeight: 600, fontSize: 15 }}>Phone Number</span>}
                name="phone"
              >
                <Input
                  placeholder="+91-9876543210"
                  style={{ borderRadius: 10, height: 46, fontSize: 15 }}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label={<span style={{ fontWeight: 600, fontSize: 15 }}>City</span>}
                name="city"
              >
                <Input
                  placeholder="Mumbai"
                  style={{ borderRadius: 10, height: 46, fontSize: 15 }}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label={<span style={{ fontWeight: 600, fontSize: 15 }}>State</span>}
                name="state"
              >
                <Input
                  placeholder="Maharashtra"
                  style={{ borderRadius: 10, height: 46, fontSize: 15 }}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label={<span style={{ fontWeight: 600, fontSize: 15 }}>Country</span>}
                name="country"
              >
                <Input
                  placeholder="India"
                  style={{ borderRadius: 10, height: 46, fontSize: 15 }}
                />
              </Form.Item>
            </Col>

            <Col span={24}>
              <Form.Item
                label={<span style={{ fontWeight: 600, fontSize: 15 }}>Address</span>}
                name="address"
              >
                <Input.TextArea
                  rows={3}
                  placeholder="Enter your complete address"
                  style={{ borderRadius: 10, fontSize: 15 }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ textAlign: 'center', marginTop: '2.5rem' }}>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              style={{
                borderRadius: 10,
                padding: '0 2rem',
                height: 48,
                fontWeight: 600,
                fontSize: 16,
                backgroundColor: '#16a34a', // Green color
                border: 'none',
              }}
            >
              Save Profile
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Profile;
