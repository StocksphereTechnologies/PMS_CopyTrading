import React, { useState } from "react";
import {
  Card,
  Col,
  Form,
  Input,
  Row,
  Typography,
  Space,
  Button,
  Select,
  message,
} from "antd";

const { Title, Text } = Typography;
const { Option } = Select;

const Payment: React.FC = () => {
  const [method, setMethod] = useState<"UPI" | "NETBANKING">("UPI");
  const [form] = Form.useForm();

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      message.success("Saved (demo) — form is valid.");
      console.log("Form values:", values);
    } catch (err) {
      console.log("Validation failed:", err);
    }
  };

  return (
    <div style={{ background: "#f6f8fb", minHeight: "100vh", padding: 24 }}>
      {/* Main white panel box full width */}
      <Card
        style={{
          border: "1px solid #e6ebf1",
          borderRadius: 8,
          background: "#ffffff",
          maxWidth: 1600,
          margin: "0 auto",
        }}
        styles={{ body: { padding: 32 } }}
      >
        <Title level={3} style={{ color: "#008080", marginBottom: 8 }}>
          Add new payment request
        </Title>
        <Text type="secondary">
          Once you have made a payment, submit a payment request to inform us.
        </Text>

        <Card
          style={{
            marginTop: 24,
            border: "1px solid #e6ebf1",
            borderRadius: 8,
            background: "#fafafa",
          }}
          styles={{ body: { padding: 24 } }}
        >
          <Row gutter={[32, 32]}>
            {/* Left: Form */}
            <Col xs={24} lg={10} xl={9}>
              <Form
                form={form}
                layout="vertical"
                initialValues={{
                  method: "UPI",
                  amount: "",
                  refNo: "",
                }}
              >
                <Form.Item
                  label="Method"
                  name="method"
                  rules={[{ required: true }]}
                >
                  <Select
                    value={method}
                    onChange={(val: "UPI" | "NETBANKING") => {
                      setMethod(val);
                      form.setFieldsValue({ method: val });
                    }}
                  >
                    <Option value="UPI">UPI</Option>
                    <Option value="NETBANKING">NETBANKING</Option>
                  </Select>
                </Form.Item>

                {/* Amount (always shown, validated numeric) */}
                <Form.Item
                  label="Amount"
                  name="amount"
                  rules={[
                    
                    {
                      validator: (_, value) => {
                        if (value === undefined || value === null || value === "") {
                          return Promise.reject("Please enter amount");
                        }
                        // Allow integers or decimals (e.g. 100 or 100.50)
                        const numericRe = /^\d+(\.\d+)?$/;
                        if (!numericRe.test(String(value).trim())) {
                          return Promise.reject("The value must be numeric");
                        }
                        return Promise.resolve();
                      },
                    },
                  ]}
                >
                  <Input
                    placeholder="Amount"
                    inputMode="decimal"
                    pattern="^\d+(\.\d+)?$"
                  />
                </Form.Item>

                {/* Ref. No. - EXACTLY 4 characters */}
                <Form.Item
                  label="Ref. No."
                  name="refNo"
                  rules={[
                    { required: true, message: "Please enter reference number" },
                    {
                      len: 4,
                      message: "Reference number must be 4 characters.",
                    },
                  ]}
                >
                  <Input placeholder="Last 4 digits of UPI/UTR/IMPS Ref. No." />
                </Form.Item>

                <Form.Item label="Comments" name="comments">
                  <Input placeholder="[Optional]" />
                </Form.Item>
              </Form>
            </Col>

            {/* Right Side - Conditional Rendering */}
            <Col xs={24} lg={14} xl={15}>
              {method === "UPI" ? (
                <Row gutter={[24, 24]} justify="center">
                  {/* Primary QR */}
                  <Col xs={24} sm={12}>
                    <Space
                      direction="vertical"
                      size={12}
                      style={{ width: "100%", alignItems: "center" }}
                    >
                      <Title level={4} style={{ color: "#008080", margin: 0 }}>
                        Primary Account
                      </Title>
                      <div
                        style={{
                          width: "100%",
                          maxWidth: 300,
                          background: "#f9fafb",
                          padding: 12,
                          borderRadius: 8,
                          border: "1px solid #e6ebf1",
                          textAlign: "center",
                        }}
                      >
                        <img
                          src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=primary"
                          alt="Primary Account QR"
                          style={{ width: "100%", height: "auto", maxWidth: 260 }}
                        />
                      </div>
                    </Space>
                  </Col>

                  {/* Backup QR */}
                  <Col xs={24} sm={12}>
                    <Space
                      direction="vertical"
                      size={12}
                      style={{ width: "100%", alignItems: "center" }}
                    >
                      <Title level={4} style={{ color: "#6b7280", margin: 0 }}>
                        Backup Account
                      </Title>
                      <div
                        style={{
                          width: "100%",
                          maxWidth: 300,
                          background: "#f9fafb",
                          padding: 12,
                          borderRadius: 8,
                          border: "1px solid #e6ebf1",
                          textAlign: "center",
                        }}
                      >
                        <img
                          src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=backup"
                          alt="Backup Account QR"
                          style={{ width: "100%", height: "auto", maxWidth: 260 }}
                        />
                      </div>
                    </Space>
                  </Col>
                </Row>
              ) : (
                <Row gutter={[24, 24]}>
                  {/* Primary NetBanking Details */}
                  <Col xs={24} sm={12}>
                    <Title
                      level={4}
                      style={{ color: "#008080", marginBottom: 12 }}
                    >
                      Primary Account
                    </Title>
                    <Form layout="vertical">
                      <Form.Item label="Name">
                        <Input value="Stocks Developer" disabled />
                      </Form.Item>
                      <Form.Item label="Account Type">
                        <Input value="Current" disabled />
                      </Form.Item>
                      <Form.Item label="Account Number">
                        <Input value="44242684883" disabled />
                      </Form.Item>
                      <Form.Item label="IFSC">
                        <Input value="SBIN0014729" disabled />
                      </Form.Item>
                    </Form>
                  </Col>

                  {/* Backup NetBanking Details */}
                  <Col xs={24} sm={12}>
                    <Title
                      level={4}
                      style={{ color: "#6b7280", marginBottom: 12 }}
                    >
                      Backup Account
                    </Title>
                    <Form layout="vertical">
                      <Form.Item label="Name">
                        <Input value="Stocks Developer" disabled />
                      </Form.Item>
                      <Form.Item label="Account Type">
                        <Input value="Current" disabled />
                      </Form.Item>
                      <Form.Item label="Account Number">
                        <Input value="44242684883" disabled />
                      </Form.Item>
                      <Form.Item label="IFSC">
                        <Input value="SBIN0014729" disabled />
                      </Form.Item>
                    </Form>
                  </Col>
                </Row>
              )}
            </Col>

            {/* Full-width Note Section */}
            <Col span={24}>
              <div style={{ marginTop: 16, lineHeight: 1.8 }}>
                <Text style={{ color: "#ef4444", fontWeight: 600 }}>Note: </Text>
                <Text style={{ color: "#ef4444" }}>
                  The system automatically recharges a{" "}
                  <span style={{  fontWeight: 600 }}>live</span>{" "}
                  account when it expires. To avoid billing for the accounts
                  which you do not use, kindly mark them as{" "}
                  <span style={{ color: "#ef4444", fontWeight: 600 }}>
                    non-live
                  </span>{" "}
                  from menu (Settings → Pseudo Accounts). To understand pricing
                  & payment,{" "}
                  <a href="#" style={{ color: "#ef4444", fontWeight: 600 }}>
                    please click here!
                  </a>
                </Text>
              </div>
            </Col>
          </Row>
        </Card>

        {/* Save button bottom right */}
        <div style={{ textAlign: "right", marginTop: 32 }}>
          <Button
            type="primary"
            style={{
              background: "#008080",
              borderColor: "#008080",
              padding: "6px 24px",
              fontWeight: 600,
            }}
            onClick={handleSave}
          >
            Save
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default Payment;
