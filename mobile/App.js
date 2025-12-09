import React, { useState, useEffect } from "react";
import { SafeAreaView, View, Text, TextInput, Button, FlatList, StyleSheet } from "react-native";
import axios from "axios";

const api = axios.create({
  baseURL: "http://10.0.2.2:8000", // android emulator to host
});

export default function App() {
  const [token, setToken] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pets, setPets] = useState([]);

  async function handleLogin() {
    const form = new FormData();
    form.append("username", email);
    form.append("password", password);
    const res = await api.post("/auth/token", form);
    const t = res.data.access_token;
    setToken(t);
    api.defaults.headers.common["Authorization"] = `Bearer ${t}`;
    loadPets();
  }

  async function loadPets() {
    try {
      const res = await api.get("/pets");
      setPets(res.data);
    } catch (e) {
      console.log("Failed to load pets", e.message);
    }
  }

  if (!token) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.title}>RescueWorks Mobile</Text>
        <TextInput
          style={styles.input}
          placeholder="Email"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />
        <Button title="Sign in" onPress={handleLogin} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Pets in org</Text>
      <FlatList
        data={pets}
        keyExtractor={item => String(item.id)}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.petName}>{item.name}</Text>
            <Text>{item.species} - {item.status}</Text>
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24 },
  title: { fontSize: 24, marginBottom: 16 },
  input: { borderWidth: 1, borderColor: "#ccc", marginBottom: 12, padding: 8, borderRadius: 4 },
  card: { padding: 12, borderWidth: 1, borderColor: "#ddd", borderRadius: 6, marginBottom: 8 },
  petName: { fontSize: 18, fontWeight: "600" },
});
