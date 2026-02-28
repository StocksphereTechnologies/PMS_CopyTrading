import React, { useState } from "react";
import {
  Input,
  Button,
  Row,
  Col,
  Tooltip,
  Select,
} from "antd";
import { SearchOutlined } from "@ant-design/icons";
import NotificationsTable from "./NotificationsTable";

const { Option } = Select;

const Notifications: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const [titleFilter, setTitleFilter] = useState<string | undefined>();

  return (
    <div style={{ padding: 16 }}>

      <Row gutter={8} style={{ marginBottom: 8 }}>
        <Col>
          <Tooltip title="Reset notifications filter">
            <Button
              style={{ background: "#6e6e6e", color: "#fff" }}
              onClick={()=>{
                setSearchText("");
                setTitleFilter(undefined);
              }}
            >
              Reset
            </Button>
          </Tooltip>
        </Col>
      </Row>

      <Row gutter={8} style={{ marginBottom: 8 }}>
        <Col>
          <Tooltip title="Download in Excel format">
            <Button
              style={{
                fontWeight: "bold",
                backgroundColor: "#36454F",
                color: "#fff",
              }}
            >
            Excel
            </Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Download in Csv format">
            <Button
              style={{
                fontWeight: "bold",
                backgroundColor: "#36454F",
                color: "#fff",
              }}
            >
            CSV
            </Button>
          </Tooltip>
        </Col>

        <Col flex="auto" />

        <Col>
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search"
            style={{ width: 220 }}
            value={searchText}
            onChange={(e)=>setSearchText(e.target.value)}
          />
        </Col>
      </Row>

      <NotificationsTable searchText={searchText}/>
    </div>
  );
};

export default Notifications;
