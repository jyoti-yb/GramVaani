import { Navbar } from '@/components/Navbar';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect, useState } from 'react';
import { notificationAPI } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from '@/hooks/use-toast';



export const NotificationsPage = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (user?.username) {
      notificationAPI
        .getUserNotifications(user.username)
        .then((res) => setNotifications(res.data))
        .catch(() => toast({ title: 'Failed to load notifications' }));
    }
  }, [user]);

  return (
    <div className="min-h-screen bg-background">
      <Navbar /> {/* Add Navbar like in your Feedback page */}

      <div className="container mx-auto px-6 py-12 max-w-4xl">
        <h1 className="text-3xl font-bold mb-6">Notifications</h1>
        {notifications.length === 0 ? (
          <p className="text-muted-foreground">No notifications yet.</p>
        ) : (
          <div className="grid gap-4">
            {notifications.map((n, idx) => (
              <Card key={idx} className="hover:shadow-lg transition">
                <CardContent className="p-4">
                  <h2 className="text-lg font-semibold">{n.title}</h2>
                  <p className="text-sm text-muted-foreground mt-1">{n.message}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    From: <span className="font-medium">{n.sender}</span> |{' '}
                    {new Date(n.timestamp).toLocaleString()}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
