import React, { useEffect, useState, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";
import { groupAPI, CHAT_WS_URL } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import SockJS from "sockjs-client";
import { over } from "stompjs";

interface ChatGroup {
  id: number;
  groupName: string;
  teamMate: string;
}

interface ChatMessage {
  groupName: string;
  sender: string;
  content: string;
  messageType: string;
  timestamp: string;
}

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [groups, setGroups] = useState<ChatGroup[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<ChatGroup | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const stompClientRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch groups
  useEffect(() => {
    if (user) {
      groupAPI
        .getAllGroups(user.username)
        .then((res) => setGroups(res.data))
        .catch((err) => console.error("Error fetching chat groups:", err))
        .finally(() => setLoading(false));
    }
  }, [user]);

  // Connect to WebSocket
  useEffect(() => {
    const socket = new SockJS(CHAT_WS_URL); // Use HTTP/HTTPS URL for SockJS
    const stompClient = over(socket);
    stompClient.connect({}, () => {
      console.log("Connected to WebSocket");
    });
    stompClientRef.current = stompClient;

    return () => {
      if (stompClientRef.current) {
        stompClientRef.current.disconnect(() => console.log("Disconnected WebSocket"));
      }
    };
  }, []);

  // Fetch and subscribe messages for selected group
  useEffect(() => {
    if (!selectedGroup || !stompClientRef.current) return;

    // Fetch initial messages via REST
    fetch(`/chat/${selectedGroup.groupName}`)
      .then((res) => res.json())
      .then((data) => setMessages(data))
      .catch((err) => console.error(err));

    // Subscribe to WebSocket topic
    const subscription = stompClientRef.current.subscribe(
      `/topic/group/${selectedGroup.groupName}`,
      (msg: any) => {
        const newMessage = JSON.parse(msg.body);
        setMessages((prev) => [...prev, newMessage]);
      }
    );

    return () => {
      subscription.unsubscribe();
      setMessages([]); // clear messages when switching groups
    };
  }, [selectedGroup]);

  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Send message
  const sendMessage = () => {
    if (!newMessage.trim() || !selectedGroup || !user) return;

    const messagePayload = {
      groupName: selectedGroup.groupName,
      sender: user.username,
      content: newMessage,
      messageType: "CHAT",
    };

    stompClientRef.current.send(
      "/app/chat.sendMessage",
      {},
      JSON.stringify(messagePayload)
    );

    setNewMessage(""); // clear input
  };

  if (loading)
    return (
      <div className="text-center mt-10 text-muted-foreground">
        Loading chats...
      </div>
    );

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Navbar />

      <div className="flex flex-1 gap-4 p-6">
        {/* Left: Groups List */}
        <div className="w-64 flex-shrink-0 bg-card p-4 rounded-xl shadow-md space-y-2 overflow-y-auto">
          {groups.length === 0 ? (
            <p className="text-muted-foreground">No projects found</p>
          ) : (
            groups.map((group) => (
              <button
                key={group.id}
                onClick={() => setSelectedGroup(group)}
                className={`w-full text-left p-3 rounded-lg transition
                  ${selectedGroup?.id === group.id ? "bg-primary/20" : "hover:bg-primary/10"}`}
              >
                <h3 className="font-semibold">{group.groupName}</h3>
                <p className="text-sm text-muted-foreground">
                  Team: {group.teamMate}
                </p>
              </button>
            ))
          )}
        </div>

        {/* Right: Chat Panel */}
        <div className="flex-1 bg-card p-4 rounded-xl shadow-md flex flex-col">
          {selectedGroup ? (
            <>
              <h3 className="text-2xl font-bold">{selectedGroup.groupName}</h3>

              {/* Messages */}
              <div className="flex-1 mt-4 overflow-y-auto space-y-2">
                {messages.length === 0 ? (
                  <p className="text-muted-foreground">No messages yet</p>
                ) : (
                  messages.map((msg, idx) => (
                    <div key={idx} className="p-2 rounded-lg bg-primary/10">
                      <strong>{msg.sender}:</strong> {msg.content}
                      <div className="text-xs text-muted-foreground">
                        {msg.timestamp}
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Box */}
              <div className="mt-4 flex gap-2">
                <input
                  type="text"
                  className="flex-1 p-2 rounded-lg border border-gray-300"
                  placeholder="Type a message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") sendMessage();
                  }}
                />
                <button
                  className="bg-primary text-white px-4 rounded-lg"
                  onClick={sendMessage}
                >
                  Send
                </button>
              </div>
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-muted-foreground text-lg">
              Select a project to view
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
