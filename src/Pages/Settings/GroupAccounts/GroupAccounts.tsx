import React, { useState, useEffect } from "react";
import { Button, Input, Row, Col, Tooltip } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import GroupsTable from "./GroupsTable";
import { useNavigate } from "react-router-dom";
import { groupService } from "../../../Services/groupService";

const tealBtn = { background: "#0bb", color: "#fff" };

interface GroupData {
  id: number;
  key: number;
  name: string;
  multiplier: number;
  description: string;
  totalAccounts: number;
}

const GroupAccounts: React.FC = () => {

  const [searchText, setSearchText] = useState("");
  const [groups, setGroups] = useState<GroupData[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const res = await groupService.getAll();
      console.log("Groups API Response:", res);
      setGroups(res);
    } catch (error) {
      console.error("Failed to fetch groups", error);
    }
  };

  return (
    <div style={{ padding: 16 }}>

      <h2>Group Accounts</h2>

      <p style={{ color: "#c45a00", marginBottom: 12 }}>
        A list of all your group accounts configured with AutoTrader
      </p>

      <Row gutter={8} style={{ marginBottom: 12 }}>

        <Col>
          <Tooltip title="Create a Trading Account">
            <Button
              style={tealBtn}
              onClick={() =>
                navigate("/settings/groupaccounts/creategroupaccount")
              }
            >
              Create
            </Button>
          </Tooltip>
        </Col>
        <Col flex="auto" />
        <Col>
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 220 }}
          />
        </Col>
      </Row>
      <GroupsTable
        searchText={searchText}
        data={groups}
      />
    </div>
  );
};

export default GroupAccounts;

