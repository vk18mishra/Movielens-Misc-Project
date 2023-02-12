import streamlit as st
import plotly.graph_objects as go

def paged_list_using_session(data, N, N_tot):
                
            if(N_tot>10):
                # N = 10
                if "page" not in st.session_state:
                    st.session_state.page = 0
                last_page = len(data) // N

                # Add a next button and a previous button

                prev, _ ,next = st.columns([4, 15, 4])

                if next.button("Next"):

                    if st.session_state.page + 1 > last_page:
                        st.session_state.page = 0
                    else:
                        st.session_state.page += 1

                if prev.button("Previous"):

                    if st.session_state.page - 1 < 0:
                        st.session_state.page = last_page
                    else:
                        st.session_state.page -= 1

                # Get start and end indices of the next page of the dataframe
                start_idx = st.session_state.page * N 
                end_idx = (1 + st.session_state.page) * N

                # Index into the sub dataframe
                sub_df = data.iloc[start_idx:end_idx]

                fig = go.Figure(
                    data=[
                        go.Table(
                            columnwidth = [0.5,0.8,0.5],
                            header=dict(
                                values=[f"<b>{i}</b>" for i in sub_df.columns.to_list()],
                                fill_color='pink'
                                ),
                            cells=dict(
                                values=sub_df.transpose()
                                )
                            )
                        ]
                    )
                st.plotly_chart(fig, use_container_width=True)
            # If total matches is less than or equal to 10 then just show them normally on one page
            elif(N_tot<=10):
                fig = go.Figure(
                    data=[
                        go.Table(
                            columnwidth = [0.5,0.8,0.5],
                            header=dict(
                                values=[f"<b>{i}</b>" for i in data.columns.to_list()],
                                fill_color='pink'
                                ),
                            cells=dict(
                                values=data.transpose()
                                )
                            )
                        ]
                    )
                st.plotly_chart(fig, use_container_width=True)