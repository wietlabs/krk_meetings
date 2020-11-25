import * as React from "react";
import { Alert, View } from "react-native";
import { Button, TextInput } from "react-native-paper";
import { getNickname } from "../../../UserManager";
import { createMeeting } from "../../../api/MeetingsApi";

export default function CreateMeetingScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;

  const [name, setName] = React.useState("");
  const [nickname, setNickname] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);

  const nameRef = React.useRef();
  const nicknameRef = React.useRef();

  navigation.addListener("focus", () => {
    nameRef.current.focus();
    suggestNickname();
  });

  const suggestNickname = async () => {
    if (!nickname) {
      const nickname = await getNickname(userUuid);
      setNickname(nickname);
    }
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
    if (!nickname) {
      showError("Proszę wpisać pseudonim", nicknameRef);
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

    const { uuid: meetingUuid } = await createMeeting({
      userUuid,
      nickname,
      name,
    });

    navigation.replace("MeetingDetails", { userUuid, meetingUuid });
  };

  return (
    <View style={{ padding: 16 }}>
      <TextInput
        ref={nameRef}
        label="Nazwa spotkania"
        value={name}
        left={<TextInput.Icon name="calendar-text-outline" />}
        onChangeText={(name) => setName(name)}
        style={{ backgroundColor: "white", marginBottom: 16 }}
      />
      <TextInput
        ref={nicknameRef}
        label="Pseudonim"
        value={nickname}
        left={<TextInput.Icon name="account-outline" />}
        onChangeText={(nickname) => setNickname(nickname)}
        style={{ backgroundColor: "white", marginBottom: 16 }}
      />
      <Button mode="contained" loading={submitting} onPress={handleSubmit}>
        Utwórz spotkanie
      </Button>
    </View>
  );
}
