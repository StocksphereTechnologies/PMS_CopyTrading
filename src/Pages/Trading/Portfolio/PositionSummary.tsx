import React from "react";
import { Card, Row, Col } from "antd";

const PositionSummary = ({ positions }: any) => {

  const m2m = positions.reduce((s: number, p: any) => s + Number(p.m2m || 0), 0);
  const pnl = positions.reduce((s: number, p: any) => s + Number(p.pnl || 0), 0);
  const atPnl = positions.reduce((s: number, p: any) => s + Number(p.atpnl || 0), 0);

  const longCount = positions.filter((p: any) => p.direction === "LONG").length;
  const shortCount = positions.filter((p: any) => p.direction === "SHORT").length;
  const neutralCount = positions.filter((p: any) => p.direction === "NEUTRAL").length;

  const openCount = positions.filter((p: any) => p.netqty !== 0).length;
  const closedCount = positions.filter((p: any) => p.netqty === 0).length;

  const netQtyL = positions
    .filter((p: any) => p.netqty > 0)
    .reduce((s: number, p: any) => s + p.netqty, 0);

  const netQtyS = positions
    .filter((p: any) => p.netqty < 0)
    .reduce((s: number, p: any) => s + Math.abs(p.netqty), 0);

  const total = positions.length;
  const accounts = new Set(positions.map((p: any) => p.accid)).size;

  return (
    <div style={{ width: "95%", margin: "24px auto" }}>
      <Card
        title={
          <span style={{ color: "#00968f", fontWeight: "bold" }}>
            POSITIONS SUMMARY
          </span>
        }
        style={{
          background: "#f4faff",
          border: "1px solid #d9d9d9",
        }}
      >
        <Row gutter={[16, 8]}>
          <Col lg={4}>
            <div><strong>» M2M</strong> = <strong>{m2m.toFixed(2)}</strong></div>
            <div><strong>» PnL</strong> = <strong>{pnl.toFixed(2)}</strong></div>
            <div><strong>» AT PnL</strong> = <strong>{atPnl.toFixed(2)}</strong></div>
          </Col>

          <Col lg={4}>
            <div>» Long = {longCount}</div>
            <div>» Short = {shortCount}</div>
            <div>» Neutral = {neutralCount}</div>
          </Col>

          <Col lg={4}>
            <div>» Open = {openCount}</div>
            <div>» Closed = {closedCount}</div>
          </Col>

          <Col lg={4}>
            <div>» NetQty-L = {netQtyL}</div>
            <div>» NetQty-S = {netQtyS}</div>
          </Col>

          <Col lg={4}>
            <div>» Total = {total}</div>
            <div>» Accounts = {accounts}</div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default PositionSummary;
