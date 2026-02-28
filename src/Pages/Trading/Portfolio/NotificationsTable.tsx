import React, { useState } from "react";
import { Table, Select } from "antd";

const { Option } = Select;

const initialData: any[] = [];

const columns = [
  { 
    title: "Time", 
    dataIndex: "time", 
    sorter: (a:any,b:any)=>a.time.localeCompare(b.time) 
  },
  { 
    title: "Pse Acc", 
    dataIndex: "pseAcc", 
    sorter: (a:any,b:any)=>a.pseAcc.localeCompare(b.pseAcc) 
  },
  {
    title: "Trd Acc", 
    dataIndex: "trdAcc", 
    sorter: (a:any,b:any)=>a.trdAcc.localeCompare(b.trdAcc) 
  },
  {
    title: "Title", 
    dataIndex: "title", 
    sorter: (a:any,b:any)=>a.title.localeCompare(b.title) 
  },
  { 
    title: "Message", 
    dataIndex: "message", 
    sorter: (a:any,b:any)=>a.message.localeCompare(b.message) 
  },
  { 
    title: "Broker", 
    dataIndex: "broker", 
    sorter: (a:any,b:any)=>a.broker.localeCompare(b.broker) 
  },
  { 
    title: "Category", 
    dataIndex: "category", 
    sorter: (a:any,b:any)=>a.category.localeCompare(b.category) 
  },
  { 
    title: "Command Id", 
    dataIndex: "commandid", 
    sorter: (a:any,b:any)=>a.commandid.localeCompare(b.commandid) 
  },
  { 
    title: "Id", 
    dataIndex: "id", 
    sorter: (a:any,b:any)=>a.id.localeCompare(b.id) 
  },
];

const NotificationsTable: React.FC<any> = ({ searchText }) => {
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [filteredData, setFilteredData] = useState(initialData);

  const handleColumnFilter = (value: string, key: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);

    let data = initialData;

    Object.keys(newFilters).forEach((k) => {
      if (newFilters[k]) {
        data = data.filter((row:any) =>
          String(row[k]).toLowerCase().includes(newFilters[k].toLowerCase())
        );
      }
    });

    if (searchText) {
      data = data.filter((row:any)=>
        Object.values(row).some(v =>
          String(v).toLowerCase().includes(searchText.toLowerCase())
        )
      );
    }

    setFilteredData(data);
  };

  const filterRow = (
    <tr>
      {columns.map((col:any)=>(
        <th key={col.dataIndex}>
          <Select
            allowClear
            size="small"
            style={{ width: "100%" }}
            value={filters[col.dataIndex]}
            onChange={(v)=>handleColumnFilter(v||"", col.dataIndex)}
          />
        </th>
      ))}
    </tr>
  );

  return (
    <Table
      bordered
      pagination={false}
      columns={columns}
      dataSource={filteredData}
      scroll={{ x: "max-content" }}
      locale={{ emptyText: "" }}
      components={{
        header: {
          wrapper: (props:any)=>(
            <thead {...props}>
              {props.children}
              {filterRow}
            </thead>
          ),
        },
        body: {
          wrapper: (props:any)=>
            filteredData.length === 0 ? (
              <tbody>
                <tr>
                  <td colSpan={columns.length} style={{ textAlign:"center", fontWeight:"bold" }}>
                    No data available in table
                  </td>
                </tr>
              </tbody>
            ) : <tbody {...props}/>
        },
      }}
    />
  );
};

export default NotificationsTable;
