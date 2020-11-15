import * as React from "react";
import { Alert, ScrollView, RefreshControl, View, Text } from "react-native";
import { Card, Chip, List, RadioButton, Button } from "react-native-paper";
import {
  validateUuid,
  getMeetingOwnerNickname,
  createRandomNickname,
} from "../../utils";
import {
  checkIfMeetingExists,
  getMeeting,
  joinMeeting,
} from "../../api/MeetingsApi";
import Placeholder from "../../components/Placeholder";
import { loadUsers } from "../../UserManager";

export default function JoinMeetingScreen({ navigation, route }) {
  const meetingUuid = route.params.meetingUuid;
  // const meetingUuid = "960fb91d-7a25-4dcc-acb5-1fc16f6579ff";

  const [refreshing, setRefreshing] = React.useState(false);
  const [meeting, setMeeting] = React.useState(null);
  const [users, setUsers] = React.useState([]);
  const [userUuid, setUserUuid] = React.useState(null);

  const refreshMeeting = async () => {
    if (meetingUuid) {
      setRefreshing(true);
      const meeting = await getMeeting(meetingUuid);
      setMeeting(meeting);
      setRefreshing(false);
    }
  };

  const refreshUsers = async () => {
    const users = await loadUsers();
    setUsers(users);
    if (users.length == 1) setUserUuid(users[0].uuid);
  };

  const handleRefresh = async () => {
    refreshMeeting();
    refreshUsers();
  };

  React.useEffect(() => {
    handleRefresh();
  }, []);

  const showError = (message) => {
    Alert.alert("Wystąpił błąd", message);
  };

  const validate = () => {
    if (!userUuid) {
      showError("Proszę wybrać tożsamość");
      return false;
    }

    return true;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    const meetingExists = await checkIfMeetingExists(meetingUuid);
    if (!meetingExists) {
      showError("Nie znaleziono spotkania o podanym identyfikatorze.");
      return;
    }

    const nickname = createRandomNickname(); // TODO: user?.nickname

    try {
      await joinMeeting({ meetingUuid, userUuid, nickname });
    } catch (e) {
      const error = e.response.data["error"];
      if (error == "Already a member") {
        showError("Jesteś już członkiem tego spotkania");
      } else {
        showError(error);
        return;
      }
    }

    navigation.pop(2);
    navigation.push("Meetings", { userUuid: userUuid });
    navigation.navigate("MeetingDetails", {
      userUuid: userUuid,
      meetingUuid: meetingUuid,
    });
  };

  if (!validateUuid(meetingUuid)) {
    return (
      <Placeholder icon="calendar-question" text="Nie znaleziono spotkania" />
    );
  }

  return (
    <ScrollView
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {meeting && (
        <View style={{ margin: 16 }}>
          <Card style={{ marginBottom: 8 }}>
            <Card.Title
              title={meeting.name}
              subtitle={meeting.uuid}
              subtitleStyle={{ fontSize: 14, letterSpacing: 0 }}
            />
            <Card.Content style={{ flexDirection: "row" }}>
              <Chip icon="account-multiple" style={{ marginRight: 8 }}>
                {meeting.members.length}
              </Chip>
              <Chip icon="crown">{getMeetingOwnerNickname(meeting)}</Chip>
            </Card.Content>
          </Card>
          <RadioButton.Group value={userUuid} onValueChange={setUserUuid}>
            {users.map(({ uuid, nickname }) => (
              <List.Item
                key={uuid}
                onPress={() => setUserUuid(uuid)}
                title={nickname === null ? "Tożsamość bez nazwy" : nickname}
                titleStyle={nickname === null ? { opacity: 0.2 } : null}
                description={uuid}
                left={(props) => (
                  <View style={{ marginTop: 8 }}>
                    <RadioButton {...props} value={uuid} color="deepskyblue" />
                  </View>
                )}
              />
            ))}
          </RadioButton.Group>
          {/* <TextInput
            value={nickname}
            ref={nicknameRef}
            label="Pseudonim"
            left={<TextInput.Icon name="account-badge-horizontal-outline" />}
            right={
              <TextInput.Icon name="close" onPress={() => setNickname("")} />
            }
            onChangeText={setNickname}
            style={{ backgroundColor: "white", marginBottom: 16 }}
          /> */}
          <Button
            mode="contained"
            icon="account-plus"
            color="deepskyblue"
            onPress={handleSubmit}
            style={{ marginTop: 12 }}
          >
            Dołącz do spotkania
          </Button>
        </View>
      )}
    </ScrollView>
  );
}
