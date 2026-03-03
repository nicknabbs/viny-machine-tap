-- Allow users to delete their own votes (unvote)
CREATE POLICY "Anyone can delete their own votes"
  ON votes FOR DELETE
  USING (true);

-- Enable full replica identity so DELETE realtime events include old row data
ALTER TABLE votes REPLICA IDENTITY FULL;
