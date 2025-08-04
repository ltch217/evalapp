
import careHomeysLogo from './assets/logo.png'
import './App.css'
import Form from './components/Form.jsx'

function App() {

  return (
    <>
      <div>
        <a href="https://carehomeys.com" target="_blank">
          <img src={careHomeysLogo} className="logo" alt="CH logo"/>
        </a>
      </div>
      <h1>Resume Evals</h1>
      <Form></Form>
      <div style = {{display: 'flex'}}>
      </div>
    </>
  )
}

export default App
