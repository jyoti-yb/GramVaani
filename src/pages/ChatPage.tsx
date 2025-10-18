import React, { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { groupAPI } from "@/lib/api";
import { Navbar } from "@/components/Navbar";

interface ChatGroup {
  id: number;
  groupName: string;
  teamMate: string;
}

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [groups, setGroups] = useState<ChatGroup[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<ChatGroup | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      groupAPI.getAllGroups(user.username)
        .then((res) => {
          setGroups(res.data);
        })
        .catch((err) => console.error("Error fetching chat groups:", err))
        .finally(() => setLoading(false));
    }
  }, [user]);

  if (loading)
    return <div className="text-center mt-10 text-muted-foreground">Loading chats...</div>;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Navbar />

      <div className="flex flex-1 gap-4 p-6">
        {/* Left: Project/Groups List */}
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
                <p className="text-sm text-muted-foreground">Team: {group.teamMate}</p>
              </button>
            ))
          )}
        </div>

        {/* Right: Selected Project Panel */}
        <div className="flex-1 bg-card p-4 rounded-xl shadow-md flex items-center justify-center">
          {selectedGroup ? (
            <div className="text-center">
              <h3 className="text-2xl font-bold">{selectedGroup.groupName}</h3>
              <p className="mt-2 text-foreground text-lg">Coming Soon 💬</p>
            </div>
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
