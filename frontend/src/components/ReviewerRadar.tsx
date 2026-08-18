import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from 'recharts';
import { PostReview } from '../types';

interface ReviewerRadarProps {
  review?: PostReview;
}

export const ReviewerRadar: React.FC<ReviewerRadarProps> = ({ review }) => {
  if (!review) {
    return (
      <div className="flex items-center justify-center h-64 text-xs text-slate-500">
        No evaluation rubric scores available.
      </div>
    );
  }

  const data = [
    { subject: 'Hook Impact', score: review.score_hook_impact, fullMark: 100 },
    { subject: 'Storytelling', score: review.score_storytelling, fullMark: 100 },
    { subject: 'Prof. Depth', score: review.score_professional_depth, fullMark: 100 },
    { subject: 'Clarity', score: review.score_clarity, fullMark: 100 },
    { subject: 'Engagement', score: review.score_engagement_potential, fullMark: 100 },
    { subject: 'Originality', score: review.score_originality, fullMark: 100 },
    { subject: 'Structure', score: review.score_structure, fullMark: 100 },
    { subject: 'Actionability', score: review.score_actionability, fullMark: 100 },
    { subject: 'Emotion', score: review.score_emotional_resonance, fullMark: 100 },
    { subject: 'Authenticity', score: review.score_authenticity, fullMark: 100 },
  ];

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#334155" strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fill: '#64748b', fontSize: 9 }}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.4}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#f8fafc',
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
