async function fetchRepos(username){
  try {
    const response = await fetch(`https://api.github.com/users/${username}/repos`, {
      headers: {
          'Accept': 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28'
        }
      });

      // Check if response is OK
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      // console.log('data : ',data);
      console.log('data.length : ',data.length);
      
      for(let i=0;i<data.length;i++){
        console.log(i,' : ',data[i].name);
        console.log('html_url : ',data[i].html_url);
        
      }
  } catch (error) {
    console.log('error : ',error);
  }  
}



fetchRepos("sohampirale")