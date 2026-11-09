class Logger:
    def __init__(self, state, db, pupil_id, case_id=None):
        self.state,self.db,self.pupil_id,self.case_id=state,db,pupil_id,case_id

    def action(self, agent, inputs, decision, raw=None):
        return self.state.log(self.db,self.pupil_id,self.case_id,agent,inputs,decision,raw)
