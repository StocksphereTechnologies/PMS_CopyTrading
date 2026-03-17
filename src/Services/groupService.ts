import api from "./api";

export interface Group {
  id: number;
  key: number;
  name: string;
  multiplier: number;
  description: string;
  totalAccounts: number;
  account_ids: number[];
}

export const groupService = {

  // Get all groups
  async getAll(): Promise<Group[]> {
    const res = await api.get("/groups/");

    const groups: Group[] = res.data.map((g: any) => ({
      id: g.id,
      key: g.id,
      name: g.name,
      multiplier: g.multiplier,
      description: g.description,
      account_ids: g.account_ids ?? [],
      totalAccounts: g.account_ids ? g.account_ids.length : 0
    }));

    return groups;
  },

  // Create group
  async create(data: {
    name: string;
    multiplier: number;
    description: string;
    account_ids: number[];
  }) {
    const res = await api.post("/groups/", data);
    return res.data;
  },

  // Update group
  async update(
    id: number,
    data: {
      name: string;
      multiplier: number;
      description: string;
      account_ids: number[];
    }
  ) {
    const res = await api.put(`/groups/${id}`, data);
    return res.data;
  },

  // Get group by ID
  async getById(id: number) {
    const res = await api.get(`/groups/${id}`);
    return res.data;
  },

  // Delete group
  async delete(id: number) {
    const res = await api.delete(`/groups/${id}`);
    return res.data;
  }
};



// import api from "./api";

// export interface Group {
//   id: number;
//   key: number;
//   name: string;
//   multiplier: number;
//   description: string;
//   totalAccounts: number;
//   account_ids: number[];
// }

// export const groupService = {

//   // Get all groups
//   async getAll(): Promise<Group[]> {
//     const res = await api.get("/groups/");   // important: trailing slash

//     const groups: Group[] = res.data.map((g: any) => ({
//       id: g.id,
//       key: g.id,                // required for Ant Design table
//       name: g.name,
//       multiplier: g.multiplier,
//       description: g.description,
//       account_ids: g.account_ids ?? [],
//       totalAccounts: g.account_ids ? g.account_ids.length : 0
//     }));

//     return groups;
//   },

//   // Create new group
//   async create(data: {
//     name: string;
//     multiplier: number;
//     description: string;
//     account_ids: number[];
//   }) {
//     const res = await api.post("/groups/", data);   // trailing slash
//     return res.data;
//   }

//   async update(groupId: number, data: {
//     name: string;
//     multiplier: number;
//     description: string;
//     account_ids: number[];
//   }) {
//     const res = await api.put(`/groups/${groupId}/`, data);
//     return res.data;
//   },  
// };
// import api from "./api";

// export interface Group {
//   id: number;
//   key: number;
//   name: string;
//   multiplier: number;
//   description: string;
//   totalAccounts: number;
//   account_ids: number[];
// }

// export const groupService = {

//   async getAll(): Promise<Group[]> {
//     const res = await api.get("/groups");

//     // Convert backend response to frontend format
//     const groups: Group[] = res.data.map((g: any) => ({
//       id: g.id,
//       key: g.id, // required for Ant Design tables
//       name: g.name,
//       multiplier: g.multiplier,
//       description: g.description,
//       account_ids: g.account_ids ?? [],
//       totalAccounts: g.account_ids ? g.account_ids.length : 0
//     }));

//     return groups;
//   },

//   async create(data: {
//     name: string;
//     multiplier: number;
//     description: string;
//     account_ids: number[];
//   }) {
//     const res = await api.post("/groups", data);
//     return res.data;
//   }

// };
