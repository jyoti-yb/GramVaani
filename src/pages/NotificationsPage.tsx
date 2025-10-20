import { Navbar } from '@/components/Navbar';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect, useState } from 'react';
import { notificationAPI } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Trash2 } from 'lucide-react';

export const NotificationsPage = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (user?.username) {
      loadNotifications();
    }
  }, [user]);

  const loadNotifications = async () => {
    try {
      const res = await notificationAPI.getUserNotifications(user.username);
      setNotifications(res.data);
    } catch (err) {
      toast({ title: 'Failed to load notifications' });
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await notificationAPI.deleteNotification(id);
      setNotifications(notifications.filter((n) => n.id !== id));
      toast({ title: 'Notification deleted' });
    } catch (err) {
      toast({ title: 'Failed to delete notification' });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-6 py-12 max-w-4xl">
        <h1 className="text-3xl font-bold mb-6">Notifications</h1>

        {notifications.length === 0 ? (
          <p className="text-muted-foreground">No notifications yet.</p>
        ) : (
          <div className="grid gap-4">
            {notifications.map((n) => (
              <Card key={n.id} className="hover:shadow-lg transition relative">
                <CardContent className="p-4 flex justify-between items-start">
                  <div>
                    <h2 className="text-lg font-semibold">{n.title}</h2>
                    <p className="text-sm text-muted-foreground mt-1">{n.message}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      From: <span className="font-medium">{n.sender}</span> |{' '}
                      {new Date(n.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(n.id)}
                    className="text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
