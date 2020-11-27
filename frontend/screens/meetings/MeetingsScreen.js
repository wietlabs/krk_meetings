import * as React from "react";
import { View, ScrollView, RefreshControl } from "react-native";
import { FAB, Chip, Card } from "react-native-paper";
import Loading from "../../components/Loading";
import Placeholder from "../../components/Placeholder";
import { getMeetings } from "../../api/MeetingsApi";
import { getNickname } from "../../UserManager";

export default function MeetingsScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;

  const [meetings, setMeetings] = React.useState([]);
  const [nickname, setNickname] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [refreshing, setRefreshing] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  const refresh = async () => {
    setRefreshing(true);
    await Promise.all([loadNickname(), loadMeetings()]);
    setLoading(false);
    setRefreshing(false);
  };

  const loadNickname = async () => {
    const nickname = await getNickname(userUuid);
    setNickname(nickname);
  };

  const loadMeetings = async () => {
    const meetings = await getMeetings({ userUuid });
    setMeetings(meetings);
  };

  React.useEffect(() => {
    navigation.addListener("focus", () => {
      refresh();
    });
  }, []);

  React.useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <Chip icon="account-circle" style={{ marginRight: 16 }} mode="outlined">
          {nickname || userUuid.slice(0, 8)}
        </Chip>
      ),
    });
  }, [navigation, nickname]);

  const handleCreate = () => {
    navigation.navigate("CreateMeeting", { userUuid: userUuid });
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={refresh} />
        }
      >
        <View style={{ margin: 16, marginBottom: 0 }}>
          {meetings.map((meeting) => (
            <Card
              key={meeting.uuid}
              style={{ marginBottom: 16 }}
              onPress={() =>
                navigation.navigate("MeetingDetails", {
                  userUuid: userUuid,
                  meetingUuid: meeting.uuid,
                })
              }
            >
              <Card.Title
                title={meeting.name}
                subtitle={meeting.nickname}
                right={(props) => (
                  <Chip {...props} icon="account" style={{ marginRight: 12 }}>
                    {meeting.members_count}
                  </Chip>
                )}
              />
            </Card>
          ))}
        </View>
      </ScrollView>
      {meetings.length > 0 || (
        <Placeholder icon="account-multiple" text="Brak spotkań" />
      )}
      <FAB.Group
        open={open}
        icon={open ? "arrow-left" : "plus"}
        actions={[
          {
            icon: "calendar-plus",
            label: "Utwórz nowe spotkanie",
            onPress: handleCreate,
          },
        ]}
        onStateChange={({ open }) => setOpen(open)}
        onPress={() => {}}
        fabStyle={{ backgroundColor: "chartreuse" }}
      />
    </>
  );
}
