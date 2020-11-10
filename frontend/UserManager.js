import AsyncStorage from "@react-native-async-storage/async-storage";

const key = "@users";

export const loadUsers = async () => {
  const jsonValue = await AsyncStorage.getItem(key);
  if (jsonValue != null) return JSON.parse(jsonValue);
  return [];
};

export const storeUsers = async (users) => {
  const jsonValue = JSON.stringify(users);
  await AsyncStorage.setItem(key, jsonValue);
};

export const addUser = async ({ uuid, nickname }) => {
  const users = await loadUsers();
  const newUsers = users.concat({ uuid, nickname });
  await storeUsers(newUsers);
  return newUsers;
};

export const deleteUser = async (uuid) => {
  const users = await loadUsers();
  const newUsers = users.filter((user) => user.uuid !== uuid);
  await storeUsers(newUsers);
  return newUsers;
};

export const hasUser = async (uuid) => {
  const users = await loadUsers();
  return users.some((user) => user.uuid === uuid);
};

export const getNickname = async (uuid) => {
  const users = await loadUsers();
  const user = users.find((user) => user.uuid === uuid);
  return user?.nickname;
};
