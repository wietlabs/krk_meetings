import * as React from "react";
import { Alert, KeyboardAvoidingView, View } from "react-native";
import { Button, TextInput } from "react-native-paper";
import { loadUsers, getNickname } from "../../../UserManager";
import { createMeeting } from "../../../api/MeetingsApi";
import SelectAccount from "../../../components/SelectAccount";
import { ScrollView } from "react-native-gesture-handler";

export default function CreateMeetingScreen({ navigation, route }) {
  const [name, setName] = React.useState("");
  const [users, setUsers] = React.useState([]);
  const [userUuid, setUserUuid] = React.useState(route.params.userUuid);
  const [submitting, setSubmitting] = React.useState(false);

  const nameRef = React.useRef();
  const nicknameRef = React.useRef();

  React.useEffect(() => {
    refreshUsers();
  }, []);

  navigation.addListener("focus", () => {
    nameRef.current.focus();
  });

  const refreshUsers = async () => {
    const users = await loadUsers();
    setUsers(users);
  };

  const showError = (message, fieldRef) => {
    Alert.alert("Wystąpił błąd", message, [
      { text: "OK", onPress: () => fieldRef.current.focus() },
    ]);
  };

  const validate = () => {
    if (!name) {
      showError("Proszę wpisać nazwę spotkania", nameRef);
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

    const nickname = await getNickname(userUuid);

    const { uuid: meetingUuid } = await createMeeting({
      userUuid,
      nickname,
      name,
    });

    navigation.pop();
    navigation.replace("Meetings", { userUuid });
    navigation.push("MeetingDetails", { userUuid, meetingUuid });
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, justifyContent: "flex-start", padding: 16 }}
    >
      <TextInput
        ref={nameRef}
        label="Nazwa spotkania"
        value={name}
        left={<TextInput.Icon name="calendar-text-outline" />}
        onChangeText={setName}
        style={{ backgroundColor: "white" }}
      />
      <ScrollView>
        <SelectAccount
          users={users}
          selected={userUuid}
          onChange={setUserUuid}
          color="#0088ff"
          style={{ marginVertical: 8 }}
        />
      </ScrollView>
      <Button
        mode="contained"
        icon="plus"
        color="#0088ff"
        // disabled={!name.length}
        loading={submitting}
        onPress={handleSubmit}
      >
        Utwórz spotkanie
      </Button>
      <View style={{ flex: 9999 }}></View>
    </KeyboardAvoidingView>
  );
}
