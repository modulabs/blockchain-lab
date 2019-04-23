import StudyContract from "../contracts/Study.json"
import LabContract from "../contracts/Lab.json";
import getWeb3 from "../utils/getWeb3";

const getLabDetail = async () => {
  try {
    // Get network provider and web3 instance.
    const web3 = await getWeb3();

    // Use web3 to get the user's accounts.
    const accounts = await web3.eth.getAccounts();

    // Get the contract instance.
    const networkId = await web3.eth.net.getId();
    const deployedNetwork = LabContract.networks[networkId];
    const labInstance = new web3.eth.Contract(
      LabContract.abi,
      deployedNetwork && deployedNetwork.address,
    );
    const labOwner = await labInstance.methods._labOwner().call();
    const labName = await labInstance.methods.labName().call();
    const studyAddresses = await labInstance.methods.getStudyList().call();
    const studyContracts = [];
    for(const studyAddress of studyAddresses) {
      const studyInstance = new web3.eth.Contract(
        StudyContract.abi,
        studyAddress,
      );
      const studyName = await studyInstance.methods.getStudyName().call();
      studyContracts[studyContracts.length] = { studyAddress, studyName };
    }
    return { 
      accounts, 
      studyContracts, 
      labOwner, 
      labName 
    };
  } catch (error) {
    alert(
      `Failed to load web3, accounts, or contract. Check console for details.`,
    );
    console.error(error);
    return null;
  }
};

export { getLabDetail };