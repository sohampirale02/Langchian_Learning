const axios = require("axios")

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

async function getRepoIndo(html_url){
  try {
    const {data:response}=await axios.get("https://api.github.com/repos/sohampirale/Github_Leaning")
    console.log('response : ',response);
    
  } catch (error) {
    console.log('error : ',error);
    
  }
}

async function getRepoLanguages(html_url){
  try {
    const {data:response}=await axios.get("https://api.github.com/repos/sohampirale/n8n_Clone_Full_Stack/languages")
    console.log('response : ',response);
    
  } catch (error) {
    console.log('error : ',error);
    
  }
}


async function getUserEvents(html_url){
  try {
    const {data:response}=await axios.get("https://api.github.com/users/sohampirale/events/public")
    // console.log('response : ',response);
    console.log('response.length : ',response.length);
    
    
  } catch (error) {
    console.log('error : ',error);
    
  }
}



// fetchRepos("sohampirale")
// getRepoIndo()
// getRepoLanguages()
getUserEvents()

/**
 * all repos on github => judging their level based on name field of their repo
 * based on all names of repos figuring out only the BEST or most relevent repos 
 * from those selected repos fetch their
 *          i.languages
 *          ii.readme files
 *           based on these we can judge the person even more 
 * 
 */