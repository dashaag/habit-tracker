import { startOfDay, startOfWeek, isWithinInterval } from 'date-fns';

/**
 * Calculates the number of times a habit has been completed in the current period.
 * @param {object} habit - The habit object, containing frequency_type and tracking_logs.
 * @returns {number} - The number of completions for the current period.
 */
export const calculateCurrentProgress = (habit) => {
  console.log('Habit:', habit);
  if (!habit || !habit.tracking_logs || habit.tracking_logs.length === 0) {
    return 0;
  }

  const now = new Date();
  let interval;

  switch (habit.frequency_type) {
    case 'daily': {
      const todayStart = startOfDay(now);
      interval = { start: todayStart, end: now };
      break;
    }
    case 'weekly': {
      // Assuming week starts on Sunday
      const weekStart = startOfWeek(now, { weekStartsOn: 0 });
      interval = { start: weekStart, end: now };
      break;
    }
    default:
      return 0; // or handle other frequencies if they exist
  }

  const completedLogs = habit.tracking_logs.filter(log => {
    const loggedDate = new Date(log.logged_at);
    console.log('Logged Date:', loggedDate);
    console.log('Interval:', interval);
    return isWithinInterval(loggedDate, interval);
  });

  return completedLogs.length;
};
