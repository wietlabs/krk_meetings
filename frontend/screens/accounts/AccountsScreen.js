import * as React from "react";
import { Alert, RefreshControl, ScrollView } from "react-native";
import { Divider, FAB, IconButton, List } from "react-native-paper";
import Placeholder from "../../components/Placeholder";
import { loadUsers, addUser, deleteUser } from "../../UserManager";
import { censorUuid, generateRandomNickname } from "../../utils";
import { createUserLink } from "../../LinkManager";
import { createUser } from "../../api/MeetingsApi";

export default function AccountsScreen({ navigation }) {
  const [users, setUsers] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [refreshing, setRefreshing] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  const refresh = async () => {
    setRefreshing(true);
    const users = await loadUsers();
    setUsers(users);
    setLoading(false);
    setRefreshing(false);
  };

  React.useEffect(() => {
    refresh();
  }, []);

  const handleSelect = (uuid) => {
    navigation.navigate("Meetings", { userUuid: uuid });
  };

  const handleAdd = () => {
    navigation.navigate("AddAccount");
  };

  const handleCreate = async () => {
    try {
      const { uuid } = await createUser();
      const nickname = generateRandomNickname();
      const users = await addUser({ uuid, nickname });
      setUsers(users);
    } catch (e) {
      Alert.alert(
        "Wystąpił błąd",
        "Nie można utworzyć tożsamości. Proszę spróbować ponownie"
      );
      return;
    }
  };

  const handleDelete = async (uuid) => {
    const users = await deleteUser(uuid);
    setUsers(users);
  };

  const handleConfirmDelete = (uuid) => {
    Alert.alert("Potwierdzenie", `Czy na pewno usunąć tożsamość ${uuid}?`, [
      { text: "Tak", style: "destructive", onPress: () => handleDelete(uuid) },
      { text: "Nie", style: "cancel" },
    ]);
  };

  const handleShowQR = (uuid) => {
    const link = createUserLink(uuid);
    navigation.navigate("ShowAccountQRCode", { data: link });
  };

  const handleScanQR = () => {
    navigation.navigate("ScanAccountQRCode");
  };

  return (
    <>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={refresh} />
        }
      >
        {users.map(({ uuid, nickname }) => (
          <React.Fragment key={uuid}>
            <List.Item
              title={nickname === null ? "Tożsamość bez nazwy" : nickname}
              titleStyle={nickname === null ? { opacity: 0.2 } : null}
              description={censorUuid(uuid)}
              left={(props) => (
                <List.Icon
                  {...props}
                  icon="account-circle"
                  style={{ margin: 0 }}
                />
              )}
              right={(props) => (
                <>
                  <IconButton
                    icon="qrcode"
                    onPress={() => handleShowQR(uuid)}
                    style={{ margin: 0 }}
                  />
                </>
              )}
              onPress={() => handleSelect(uuid)}
              onLongPress={() => handleConfirmDelete(uuid)}
              style={{ backgroundColor: "white" }}
            />
            <Divider />
          </React.Fragment>
        ))}
      </ScrollView>
      {!loading && !users.length && (
        <Placeholder icon="account" text="Brak tożsamości" />
      )}
      <FAB.Group
        open={open}
        icon={open ? "arrow-left" : "plus"}
        actions={[
          {
            icon: "account-plus",
            label: "Utwórz nową tożsamość",
            onPress: handleCreate,
          },
          {
            icon: "qrcode-scan",
            label: "Skanuj kod QR tożsamości",
            onPress: handleScanQR,
          },
          {
            icon: "textbox",
            label: "Wpisz identyfikator tożsamości",
            onPress: handleAdd,
          },
        ]}
        onStateChange={({ open }) => setOpen(open)}
        fabStyle={{ backgroundColor: "deepskyblue" }}
      />
    </>
  );
}
