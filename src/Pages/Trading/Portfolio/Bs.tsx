import React, { useState } from "react";
import {
  Form,
  Input,
  Radio,
  Button,
  Card,
  Select,
  Switch,
  Row,
  Col,
} from "antd";

export default function OrderForm() {
  const [qty, setQty] = useState(20);
  const [side, setSide] = useState("buy");
  const increment = () => setQty(qty + 20);
  const decrement = () => qty > 20 && setQty(qty - 20);
  
  return (
    <div style={{ width: "100%", display: "flex", justifyContent: "center", marginTop: "2rem", marginBottom: "2rem"}}>
      <Card style={{ width: "90%", padding: 20, borderRadius: 12, border: `0.25rem solid ${side === "buy" ? "#4ec362ff" : "#f03e3e"}`, transition: "0.3s ease", fontFamily: "Verdana, sans-serif"}}>
        <Form layout="vertical">

          {/* BUY / SELL */}
          <Form.Item>
            <Radio.Group defaultValue="buy" onChange={(e) => setSide(e.target.value)} value={side} style={{ display: "flex", gap: 25, fontFamily: "Verdana, sans-serif"}}>
              <Radio value="buy">BUY</Radio>
              <Radio value="sell">SELL</Radio>
            </Radio.Group>
          </Form.Item>

          {/* ORDER TYPE */}
          <Form.Item>
            <Radio.Group defaultValue="regular" style={{ display: "flex", gap: 25, fontFamily: "Verdana, sans-serif"}}>
              <Radio value="regular">REGULAR</Radio>
              <Radio value="bo">BO</Radio>
              <Radio value="co">CO</Radio>
            </Radio.Group>
          </Form.Item>

          {/* MARKET TYPE */}
          <Form.Item>
            <Radio.Group defaultValue="intraday" style={{ display: "flex", gap: 25 }}>
              <Radio value="intraday">INTRADAY</Radio>
              <Radio value="delivery">DELIVERY</Radio>
              <Radio value="normal">NORMAL</Radio>
              <Radio value="mtf">MTF</Radio>
            </Radio.Group>
          </Form.Item>

          {/* LIMIT / MARKET */}
          <Form.Item>
            <Radio.Group defaultValue="limit" style={{ display: "flex", gap: 25 }}>
              <Radio value="limit">LIMIT</Radio>
              <Radio value="market">MARKET</Radio>
              <Radio value="sl">STOP_LOSS</Radio>
              <Radio value="slm">SL_MARKET</Radio>
            </Radio.Group>
          </Form.Item>

          {/* QTY + PRICE ROW */}
          <Row gutter={20}>
            {/* Quantity */}
            <Col span={6}>
              <label>Qty</label><p style={{ fontSize: 12, color: "#888" }}>1 Lots [20]</p>
              <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 5 }}>
                <Button onClick={decrement} style={{backgroundColor: "#e03131", height:"2.7rem", color: "white", fontWeight: "800"}}>−</Button>

                <Input
                  value={qty}
                  readOnly
                  style={{ width: 60, textAlign: "center" }}
                />

                <Button onClick={increment} style={{backgroundColor: "#089981", height:"2.7rem", color: "white", fontWeight: "800"}}>+</Button>
              </div>

            </Col>

            {/* Price */}
            <Col span={6}>
              <Form.Item label="Price">
                <Input placeholder="₹0" />
              </Form.Item>
            </Col>

            {/* Trig Price */}
            <Col span={6}>
              <Form.Item label="Trig. Price">
                <Input placeholder="₹0" disabled />
              </Form.Item>
            </Col>

            {/* Disclosed Qty */}
            <Col span={6}>
              <Form.Item label="Disclosed Qty.">
                <Input placeholder="0" />
              </Form.Item>
            </Col>
          </Row>

          {/* Accounts Selector */}
          <Form.Item label="[All-accounts] selected">
            <Select
              mode="multiple"
              defaultValue={["All-accounts"]}
              style={{ width: "100%"}}
            >
              <Select.Option value="All-accounts">All-accounts</Select.Option>
              <Select.Option value="Hammer">Hammer</Select.Option>
              <Select.Option value="Nifty2lots">Nifty2lots</Select.Option>
              <Select.Option value="Nifty3lots">Nifty3lots</Select.Option>
              <Select.Option value="SingleLot">SingleLot</Select.Option>
              <Select.Option value="StockOptions">StockOptions</Select.Option>
            </Select>
          </Form.Item>

          {/* SWITCHES */}
          <Row gutter={30} style={{ marginBottom: 20 }}>
            <Col span={8}>
              <label>Group Acc</label><br />
              <Switch/>
            </Col>

            <Col span={8}>
              <label>Diff. Qty.</label><br />
              <Switch />
            </Col>

            <Col span={8}>
              <label>Multiplier</label><br />
              <Switch />
            </Col>
          </Row>

          {/* Buttons */}
          <Row style={{ display: "flex", gap: 15, fontFamily: "Verdana, sans-serif"}}>
            <Button type="primary" style={{ width: 120, background: "#089981"}}>
              BUY
            </Button>

            <Button danger style={{ width: 120, fontFamily: "Verdana, sans-serif"}}>
              Reset
            </Button>
          </Row>

        </Form>
      </Card>
    </div>
  );
}
