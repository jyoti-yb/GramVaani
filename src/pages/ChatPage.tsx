import React, { useEffect, useState, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";
import { groupAPI, api, CHAT_WS_URL } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import SockJS from "sockjs-client";
import { over } from "stompjs";

interface ChatGroup {
  id: number;
  groupName: string;
  teamMate: string;
}

interface ChatMessage {
  id?: number;
  groupName: string;
  sender: string;
  content: string;
  messageType: string;
  timestamp?: string;
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

  // 🟩 Fetch user's chat groups
  useEffect(() => {
    if (user) {
      groupAPI
        .getAllGroups(user.username)
        .then((res) => setGroups(res.data))
        .catch((err) => console.error("Error fetching chat groups:", err))
        .finally(() => setLoading(false));
    }
  }, [user]);

  // 🟩 WebSocket connection setup
  useEffect(() => {
    const socket = new SockJS(CHAT_WS_URL);
    const stompClient = over(socket);
    stompClient.connect({}, () => console.log("✅ Connected to WebSocket"));
    stompClientRef.current = stompClient;

    return () => {
      stompClientRef.current?.disconnect(() =>
        console.log("❌ Disconnected WebSocket")
      );
    };
  }, []);

  // 🟩 Load messages for selected group
  useEffect(() => {
    if (!selectedGroup || !stompClientRef.current) return;

    api
      .get(`/chat/${selectedGroup.groupName}`)
      .then((res) => setMessages(res.data))
      .catch((err) => console.error("Error loading messages:", err));

    const subscription = stompClientRef.current.subscribe(
      `/topic/group/${selectedGroup.groupName}`,
      (msg: any) => {
        const newMessage = JSON.parse(msg.body);
        setMessages((prev) => [...prev, newMessage]);
      }
    );

    return () => subscription.unsubscribe();
  }, [selectedGroup]);

  // 🟩 Smooth scroll to bottom on new message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages]);

  // 🟩 Send message
  const sendMessage = () => {
    if (!newMessage.trim() || !selectedGroup || !user) return;

    const messagePayload: ChatMessage = {
      groupName: selectedGroup.groupName,
      sender: user.username,
      content: newMessage.trim(),
      messageType: "CHAT",
    };

    stompClientRef.current.send(
      "/app/chat.sendMessage",
      {},
      JSON.stringify(messagePayload)
    );
    setNewMessage("");
  };

  // 🗓️ Format date like WhatsApp
  const formatDateLabel = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    if (date.toDateString() === today.toDateString()) return "Today";
    if (date.toDateString() === yesterday.toDateString()) return "Yesterday";

    return date.toLocaleDateString(undefined, {
      day: "numeric",
      month: "short",
      year: today.getFullYear() !== date.getFullYear() ? "numeric" : undefined,
    });
  };

  if (loading) {
    return (
      <div className="text-center mt-10 text-muted-foreground">
        Loading chats...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Navbar />
      <div className="flex flex-1 flex-col md:flex-row gap-4 p-4 md:p-6">
        {/* Sidebar */}
        <div className="w-full md:w-64 flex-shrink-0 bg-card p-4 rounded-xl shadow-md space-y-2 overflow-y-auto max-h-[calc(100vh-100px)]">
          {groups.length === 0 ? (
            <p className="text-muted-foreground text-center">No projects found</p>
          ) : (
            groups.map((group) => (
              <button
                key={group.id}
                onClick={() => setSelectedGroup(group)}
                className={`w-full text-left p-3 rounded-lg transition ${
                  selectedGroup?.id === group.id
                    ? "bg-primary/20"
                    : "hover:bg-primary/10"
                }`}
              >
                <h3 className="font-semibold">{group.groupName}</h3>
                <p className="text-sm text-muted-foreground">
                  Team: {group.teamMate}
                </p>
              </button>
            ))
          )}
        </div>

        {/* Chat Section */}
        <div className="flex-1 bg-card p-4 rounded-xl shadow-md flex flex-col">
          {selectedGroup ? (
            <>
              <h3 className="text-xl md:text-2xl font-bold text-center md:text-left mb-2">
                {selectedGroup.groupName}
              </h3>

              {/* Messages Area */}
              <div
                className="flex-1 overflow-y-auto scroll-smooth px-2 py-3 border border-border rounded-lg bg-background/70"
                style={{ maxHeight: "calc(100vh - 220px)" }}
              >
                {messages.length === 0 ? (
                  <p className="text-muted-foreground text-center mt-10">
                    No messages yet
                  </p>
                ) : (
                  (() => {
                    const groupedMessages: { [date: string]: ChatMessage[] } = {};
                    messages.forEach((msg) => {
                      const date = new Date(msg.timestamp || "").toDateString();
                      if (!groupedMessages[date]) groupedMessages[date] = [];
                      groupedMessages[date].push(msg);
                    });

                    const sortedDates = Object.keys(groupedMessages).sort(
                      (a, b) => new Date(a).getTime() - new Date(b).getTime()
                    );

                    return sortedDates.map((date, idx) => (
                      <div key={idx}>
                        {/* 🗓️ Date Separator */}
                        <div className="text-center my-3">
                          <span className="bg-gray-300 dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-xs px-3 py-1 rounded-full">
                            {formatDateLabel(date)}
                          </span>
                        </div>

                        {/* 💬 Messages */}
                        <div className="space-y-3"> {/* adds space between bubbles */}
                          {groupedMessages[date].map((msg, i) => {
                            const isMine = msg.sender === user?.username;
                            return (
                              <div
                                key={i}
                                className={`flex w-full ${
                                  isMine ? "justify-end" : "justify-start"
                                }`}
                              >
                                <div
                                  className={`max-w-[80%] md:max-w-[60%] px-4 py-2.5 rounded-2xl break-words shadow-sm ${
                                    isMine
                                      ? "bg-gradient-to-br from-green-400 to-green-600 text-white rounded-br-none"
                                      : "bg-gradient-to-br from-gray-200 to-gray-400 dark:from-gray-700 dark:to-gray-800 text-black dark:text-white rounded-bl-none"
                                  }`}
                                  style={{
                                    marginTop: "4px",
                                    marginBottom: "4px",
                                  }}
                                >
                                  <div className="text-sm font-semibold opacity-80 mb-1">
                                    {msg.sender}
                                  </div>
                                  <div className="text-base leading-snug">
                                    {msg.content}
                                  </div>
                                  {msg.timestamp && (
                                    <div className="text-[10px] text-right mt-1 opacity-70">
                                      {new Date(msg.timestamp).toLocaleTimeString([], {
                                        hour: "2-digit",
                                        minute: "2-digit",
                                      })}
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ));
                  })()
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="mt-4 flex gap-2 items-center">
                <input
                  type="text"
                  className="flex-1 p-3 rounded-full border border-border bg-background text-foreground placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Type a message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                />
                <button
                  className="bg-primary text-white px-5 py-2 rounded-full hover:bg-primary/90 transition"
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
