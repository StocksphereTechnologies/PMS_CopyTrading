import React, { useEffect, useState } from "react";
import "./Nifty.css";
import { Modal, Select, Input } from "antd";
import Positions from "../Portfolio/Positions";
import OrderForm from "../Portfolio/Bs";

const { Option } = Select;

export default function NiftyB() {
  const [open, setOpen] = useState(false);

  const [index, setIndex] = useState("NIFTY");
  const [strike, setStrike] = useState(26000);

  const [ce, setCe] = useState<any>(null);
  const [pe, setPe] = useState<any>(null);

  const [price, setPrice] = useState("₹0");

  useEffect(() => {
    fetch(`http://localhost:5001/api/options/${index}/${strike}`)
      .then((res) => res.json())
      .then((data) => {
        setCe(data.CE);
        setPe(data.PE);
      })
      .catch(() => {
        setCe(null);
        setPe(null);
      });
  }, [index, strike]);

  useEffect(() => {
    if (!ce) return;

    const fetchPrice = () => {
      fetch(`http://localhost:5001/api/price/${ce.scripcode}?exch=N`)
        .then((res) => res.json())
        .then((data) => {
          setPrice(`₹${data.ltp}`);
        })
        .catch(() => {});
    };

    fetchPrice(); 
    const interval = setInterval(fetchPrice, 1000);

    return () => clearInterval(interval);
  }, [ce]);

  return (
    <div>
      <div id="mainNB">
        <div id="tab_box">
          <div className="title">
            <h3>Nifty Breakout</h3>
          </div>

          <div className="col">
            <div style={{ width: 350 }}>
              <Select
                value={index}
                onChange={(v) => setIndex(v)}
                style={{ width: "100%", height: "3rem" }}
              >
                <Option value="NIFTY">Nifty</Option>
                <Option value="BANKNIFTY">Bank Nifty</Option>
                <Option value="SENSEX">Sensex</Option>
              </Select>
            </div>

            <div style={{ width: 350 }}>
              <Select
                value="ce"
                style={{ width: "100%", height: "3rem" }}
                options={[
                  { label: `Nifty ${strike} CE`, value: "ce" },
                  { label: `Nifty ${strike} PE`, value: "pe" },
                ]}
              />
            </div>

            <div className="price" style={{ width: 350 }}>
              <Input
                value={price}
                readOnly
                style={{
                  width: "80%",
                  height: "3rem",
                  fontSize: "1.1rem",
                  border: "1px solid black",
                  textAlign: "center",
                }}
              />
            </div>

            <div className="btns">
              <div className="buy">
                <button onClick={() => setOpen(true)}>Buy</button>
              </div>
              <div className="sell">
                <button onClick={() => setOpen(true)}>Sell</button>
              </div>
            </div>
          </div>

          <div className="options">
            <Positions />
          </div>
        </div>
      </div>

      <Modal
        open={open}
        footer={null}
        width={1000}
        onCancel={() => setOpen(false)}
      >
        <OrderForm />
      </Modal>
    </div>
  );
}
