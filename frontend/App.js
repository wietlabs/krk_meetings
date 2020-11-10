import * as React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { DefaultTheme, Provider as PaperProvider } from "react-native-paper";
import HomeScreen from "./screens/home/HomeScreen";
import ConnectionResultsScreen from "./screens/connections/results/ConnectionResultsScreen";
import ConnectionResultsPlotScreen from "./screens/connections/plot/ConnectionResultsPlotScreen";
import ConnectionDetailsScreen from "./screens/connections/details/ConnectionDetailsScreen";
import AccountsScreen from "./screens/accounts/AccountsScreen";
import AddAccountScreen from "./screens/accounts/AddAccountScreen";
import ShowAccountQRCodeScreen from "./screens/accounts/ShowAccountQRCodeScreen";
import ScanAccountQRCodeScreen from "./screens/accounts/ScanAccountQRCodeScreen";
import MeetingsScreen from "./screens/meetings/MeetingsScreen";
import MeetingDetailsScreen from "./screens/meetings/MeetingDetailsScreen";
import CreateMeetingScreen from "./screens/meetings/CreateMeetingScreen";
import JoinMeetingScreen from "./screens/meetings/JoinMeetingScreen";

const Stack = createStackNavigator();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: "#0088ff",
  },
};

export default function App() {
  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <Stack.Navigator>
          {/* <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={{ title: "Krk Meetings" }}
          />
          <Stack.Screen
            name="ConnectionResults"
            component={ConnectionResultsScreen}
            options={{ title: "Wyniki wyszukiwania" }}
          />
          <Stack.Screen
            name="ConnectionResultsPlot"
            component={ConnectionResultsPlotScreen}
            options={{ title: "Wyniki wyszukiwania" }}
          />
          <Stack.Screen
            name="ConnectionDetails"
            component={ConnectionDetailsScreen}
            options={{ title: "Szczegóły połączenia" }}
          /> */}
          <Stack.Screen
            name="Accounts"
            component={AccountsScreen}
            options={{ title: "Tożsamości" }}
          />
          <Stack.Screen
            name="AddAccount"
            component={AddAccountScreen}
            options={{ title: "Dodaj tożsamość" }}
          />
          <Stack.Screen
            name="Meetings"
            component={MeetingsScreen}
            options={{ title: "Spotkania" }}
          />
          <Stack.Screen
            name="MeetingDetails"
            component={MeetingDetailsScreen}
            options={{ title: "Spotkanie" }}
          />
          <Stack.Screen
            name="CreateMeeting"
            component={CreateMeetingScreen}
            options={{ title: "Utwórz nowe spotkanie" }}
          />
          <Stack.Screen
            name="JoinMeeting"
            component={JoinMeetingScreen}
            options={{ title: "Dołącz do spotkania" }}
          />
          <Stack.Screen
            name="ShowAccountQRCode"
            component={ShowAccountQRCodeScreen}
            options={{ title: "Kod QR" }}
          />
          <Stack.Screen
            name="ScanAccountQRCode"
            component={ScanAccountQRCodeScreen}
            options={{ title: "Skanuj kod QR" }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
}
