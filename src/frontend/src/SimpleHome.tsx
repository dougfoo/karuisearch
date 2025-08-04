import React from 'react';
import { Box, Container, Typography, Button } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';

const SimpleHome: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box textAlign="center">
        <HomeIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom>
          軽井サーチ - Karui Search
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
          Karuizawa Real Estate Search System
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button variant="contained" size="large">
            Search Properties
          </Button>
          <Button variant="outlined" size="large">
            Weekly Report
          </Button>
          <Button variant="outlined" size="large">
            All Listings
          </Button>
        </Box>
        
        <Box sx={{ mt: 4, p: 3, bgcolor: 'grey.100', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            🎉 Frontend is Working!
          </Typography>
          <Typography variant="body1">
            This is a simplified home page to test if the React app is rendering correctly.
            If you can see this, the main issues have been resolved.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default SimpleHome;