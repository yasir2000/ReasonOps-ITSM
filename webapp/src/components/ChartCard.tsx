import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend,
  Tooltip
} from 'chart.js'

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Legend, Tooltip)

export default function ChartCard({ title, labels, data, color = '#6ea8fe' }: { title: string; labels: string[]; data: number[]; color?: string }) {
  return (
    <div className="card">
      <div className="label">{title}</div>
      <Line
        data={{
          labels,
          datasets: [
            {
              label: title,
              data,
              borderColor: color,
              backgroundColor: color + '33',
              tension: 0.3,
              pointRadius: 0,
            }
          ]
        }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { x: { ticks: { color: '#8aa0d0' } }, y: { ticks: { color: '#8aa0d0' } } }
        }}
        height={180}
      />
    </div>
  )
}
