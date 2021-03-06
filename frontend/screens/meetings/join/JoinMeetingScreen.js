import * as React from "react";
import { Alert, ScrollView, RefreshControl, View } from "react-native";
import { Card, Chip, Button } from "react-native-paper";
import { validateUuid, generateRandomNickname } from "../../../utils";
import {
  checkIfMeetingExists,
  getMeetingJoinInfo,
  joinMeeting,
} from "../../../api/MeetingsApi";
import Placeholder from "../../../components/Placeholder";
import SelectAccount from "../../../components/SelectAccount";
import { loadUsers, getNickname } from "../../../UserManager";

export default function JoinMeetingScreen({ navigation, route }) {
  const meetingUuid = route.params.meetingUuid;

  const [refreshing, setRefreshing] = React.useState(false);
  const [meeting, setMeeting] = React.useState(null);
  const [users, setUsers] = React.useState([]);
  const [userUuid, setUserUuid] = React.useState(null);
  const [submitting, setSubmitting] = React.useState(false);

  const refreshMeeting = async () => {
    setRefreshing(true);
    try {
      const meeting = await getMeetingJoinInfo(meetingUuid);
      setMeeting(meeting);
    } catch (e) {
      if (e.response.status === 404) {
        setMeeting(false);
      } else {
        throw e;
      }
    }
    setRefreshing(false);
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
    if (submitting) return;
    setSubmitting(true);

    if (!validate()) {
      setSubmitting(false);
      return;
    }

    const meetingExists = await checkIfMeetingExists(meetingUuid);
    if (!meetingExists) {
      showError("Nie znaleziono spotkania o podanym identyfikatorze.");
      setSubmitting(false);
      return;
    }

    const nickname = (await getNickname(userUuid)) || generateRandomNickname();

    try {
      await joinMeeting({ meetingUuid, userUuid, nickname });
    } catch (e) {
      const error = e.response.data["error"];
      const message =
        error == "Already a member"
          ? "Jesteś już członkiem tego spotkania"
          : error;
      setSubmitting(false);
      showError(message);
      return;
    }

    navigation.pop(3);
    navigation.push("Meetings", { userUuid: userUuid });
    navigation.navigate("MeetingDetails", {
      userUuid: userUuid,
      meetingUuid: meetingUuid,
    });
  };

  if (!validateUuid(meetingUuid) || meeting === false) {
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
              subtitle={meetingUuid}
              subtitleStyle={{ fontSize: 14, letterSpacing: 0 }}
            />
            <Card.Content style={{ flexDirection: "row" }}>
              <Chip icon="account-multiple" style={{ marginRight: 8 }}>
                {meeting.members_count}
              </Chip>
              <Chip icon="crown">{meeting.owner_nickname}</Chip>
            </Card.Content>
          </Card>
          <SelectAccount
            users={users}
            selected={userUuid}
            onChange={setUserUuid}
            color="deepskyblue"
          />
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
            loading={submitting}
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
